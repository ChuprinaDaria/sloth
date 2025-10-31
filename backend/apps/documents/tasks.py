from celery import shared_task
from django.utils import timezone
from google.cloud import vision
import PyPDF2
import docx
import openpyxl
import io
import boto3
from django.conf import settings
from apps.accounts.middleware import TenantSchemaContext
from .models import Document, Photo, ProcessingJob


@shared_task(bind=True)
def process_document(self, document_id, tenant_schema):
    """
    Process document: extract text, parse content, create embeddings
    """
    with TenantSchemaContext(tenant_schema):
        try:
            document = Document.objects.get(id=document_id)
            document.processing_status = 'processing'
            document.save()

            # Download file from S3 or local storage
            file_content = _download_file(document.file_path)

            # Extract text based on file type
            if document.file_type == 'pdf':
                text = _extract_text_from_pdf(file_content)
            elif document.file_type == 'docx':
                text = _extract_text_from_docx(file_content)
            elif document.file_type == 'txt':
                text = file_content.decode('utf-8')
            elif document.file_type in ['xlsx', 'csv']:
                text = _extract_text_from_excel(file_content)
            else:
                text = ""

            # Save extracted text
            document.extracted_text = text
            document.is_processed = True
            document.processing_status = 'completed'
            document.processed_at = timezone.now()
            document.save()

            # Create embeddings (trigger another task)
            from apps.embeddings.tasks import create_embeddings
            create_embeddings.delay(
                content=text,
                source_type='document',
                source_id=document.id,
                tenant_schema=tenant_schema
            )

            return f"Document {document_id} processed successfully"

        except Exception as e:
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.save()
            raise


@shared_task(bind=True)
def process_photo(self, photo_id, tenant_schema):
    """
    Process photo: Google Vision API analysis, OCR, create embeddings
    """
    with TenantSchemaContext(tenant_schema):
        try:
            photo = Photo.objects.get(id=photo_id)
            photo.processing_status = 'processing'
            photo.save()

            # Download image from S3
            image_content = _download_file(photo.file_path)

            # Initialize Google Vision client
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=image_content)

            # Perform multiple detections
            # 1. Label detection
            labels_response = client.label_detection(image=image)
            labels = [
                {
                    'description': label.description,
                    'score': label.score
                }
                for label in labels_response.label_annotations
            ]

            # 2. Text detection (OCR)
            text_response = client.text_detection(image=image)
            text = text_response.text_annotations[0].description if text_response.text_annotations else ""

            # 3. Object detection
            objects_response = client.object_localization(image=image)
            objects = [
                {
                    'name': obj.name,
                    'score': obj.score
                }
                for obj in objects_response.localized_object_annotations
            ]

            # 4. Face detection
            faces_response = client.face_detection(image=image)
            faces = [
                {
                    'joy': face.joy_likelihood.name,
                    'sorrow': face.sorrow_likelihood.name,
                    'anger': face.anger_likelihood.name
                }
                for face in faces_response.face_annotations
            ]

            # 5. Color detection
            colors_response = client.image_properties(image=image)
            colors = [
                {
                    'color': {
                        'red': color.color.red,
                        'green': color.color.green,
                        'blue': color.color.blue
                    },
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                }
                for color in colors_response.image_properties_annotation.dominant_colors.colors
            ]

            # Save results
            photo.labels = labels
            photo.text = text
            photo.objects = objects
            photo.faces = faces
            photo.colors = colors
            photo.is_processed = True
            photo.processing_status = 'completed'
            photo.processed_at = timezone.now()
            photo.save()

            # Create embeddings from extracted text and labels
            combined_text = f"{text} {' '.join([l['description'] for l in labels])}"
            from apps.embeddings.tasks import create_embeddings
            create_embeddings.delay(
                content=combined_text,
                source_type='photo',
                source_id=photo.id,
                tenant_schema=tenant_schema
            )

            return f"Photo {photo_id} processed successfully"

        except Exception as e:
            photo.processing_status = 'failed'
            photo.processing_error = str(e)
            photo.save()
            raise


@shared_task
def cleanup_old_files():
    """
    Delete old files from storage to save space
    """
    # TODO: Implement cleanup logic based on organization settings
    pass


# Helper functions

def _download_file(file_path):
    """Download file from S3 or local storage"""
    if settings.USE_S3:
        s3 = boto3.client('s3')
        response = s3.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_path
        )
        return response['Body'].read()
    else:
        with open(file_path, 'rb') as f:
            return f.read()


def _extract_text_from_pdf(file_content):
    """Extract text from PDF"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def _extract_text_from_docx(file_content):
    """Extract text from DOCX"""
    doc = docx.Document(io.BytesIO(file_content))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def _extract_text_from_excel(file_content):
    """Extract text from Excel"""
    workbook = openpyxl.load_workbook(io.BytesIO(file_content))
    text = ""
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows(values_only=True):
            text += " ".join([str(cell) for cell in row if cell]) + "\n"
    return text
