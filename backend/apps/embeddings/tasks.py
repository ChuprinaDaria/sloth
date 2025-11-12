from celery import shared_task
from django.utils import timezone
from django.conf import settings
from apps.accounts.middleware import TenantSchemaContext
from .models import Embedding, VectorStore
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

openai.api_key = settings.OPENAI_API_KEY


@shared_task(bind=True)
def create_embeddings(self, content, source_type, source_id, tenant_schema):
    """
    Create embeddings from text content
    """
    with TenantSchemaContext(tenant_schema):
        try:
            # Get vector store settings
            vector_store = VectorStore.objects.first()
            if not vector_store:
                vector_store = VectorStore.objects.create(
                    name='Default Vector Store'
                )

            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=vector_store.chunk_size,
                chunk_overlap=vector_store.chunk_overlap,
                length_function=len,
            )

            chunks = text_splitter.split_text(content)

            # Create embeddings for each chunk
            embeddings_created = 0
            for chunk in chunks:
                if not chunk.strip():
                    continue

                # Generate embedding using OpenAI
                response = openai.embeddings.create(
                    model=vector_store.embedding_model,
                    input=chunk
                )

                vector = response.data[0].embedding

                # Create embedding record
                embedding = Embedding.objects.create(
                    source_type=source_type,
                    source_id=source_id,
                    content=chunk,
                    metadata={
                        'model': vector_store.embedding_model,
                        'chunk_index': embeddings_created
                    }
                )

                # Store vector in database (using raw SQL for pgvector)
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"UPDATE embeddings SET vector = %s::vector WHERE id = %s",
                        [vector, embedding.id]
                    )

                embeddings_created += 1

            # Update stats
            vector_store.total_embeddings = Embedding.objects.count()
            vector_store.save()

            return f"Created {embeddings_created} embeddings for {source_type}:{source_id}"

        except Exception as e:
            print(f"Error creating embeddings: {e}")
            raise


@shared_task
def rebuild_vector_store(tenant_schema):
    """
    Rebuild entire vector store (useful after changing settings)
    """
    with TenantSchemaContext(tenant_schema):
        # Delete all existing embeddings
        Embedding.objects.all().delete()

        # Re-process all documents
        from apps.documents.models import Document, Photo
        from apps.agent.models import Prompt

        # Documents
        for doc in Document.objects.filter(is_processed=True):
            create_embeddings.delay(
                content=doc.extracted_text,
                source_type='document',
                source_id=doc.id,
                tenant_schema=tenant_schema
            )

        # Photos
        for photo in Photo.objects.filter(is_processed=True):
            # Безпечно обробляємо labels (може бути None або порожнім списком)
            labels_text = ""
            if photo.labels and isinstance(photo.labels, list):
                labels_text = ' '.join([l.get('description', '') for l in photo.labels if isinstance(l, dict) and l.get('description')])
            
            combined_text = f"{photo.text or ''} {labels_text}".strip()
            
            # Створюємо ембедінги тільки якщо є контент
            if combined_text:
                create_embeddings.delay(
                    content=combined_text,
                    source_type='photo',
                    source_id=photo.id,
                    tenant_schema=tenant_schema
                )

        return "Vector store rebuild initiated"


def search_similar(query_text, tenant_schema, limit=5):
    """
    Search for similar embeddings using cosine similarity
    """
    with TenantSchemaContext(tenant_schema):
        # Generate embedding for query
        response = openai.embeddings.create(
            model='text-embedding-ada-002',
            input=query_text
        )
        query_vector = response.data[0].embedding

        # Search using pgvector cosine similarity
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, source_type, source_id, content,
                       1 - (vector <=> %s::vector) as similarity
                FROM embeddings
                ORDER BY vector <=> %s::vector
                LIMIT %s
            """, [query_vector, query_vector, limit])

            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'source_type': row[1],
                    'source_id': row[2],
                    'content': row[3],
                    'similarity': row[4]
                })

            return results
