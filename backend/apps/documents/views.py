from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import Document, Photo
from rest_framework import serializers
from .tasks import process_document, process_photo


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file_type', 'file_path', 'file_size',
            'is_processed', 'processing_status', 'extracted_text',
            'created_at'
        ]
        read_only_fields = ['file_path', 'file_size', 'is_processed', 'processing_status']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'id', 'file_path', 'file_size', 'is_processed', 'processing_status',
            'labels', 'text', 'objects', 'created_at'
        ]
        read_only_fields = ['file_path', 'file_size', 'is_processed', 'labels', 'text', 'objects']


class DocumentUploadView(generics.CreateAPIView):
    """Upload and process document"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check organization exists
        if not hasattr(request.user, 'organization') or not request.user.organization:
            return Response(
                {'error': 'User organization not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get title or use filename
        title = request.data.get('title') or (file_obj.name if file_obj.name else 'Untitled Document')

        # Determine file type
        if not file_obj.name or '.' not in file_obj.name:
            return Response(
                {'error': 'File must have an extension'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_type = file_obj.name.split('.')[-1].lower()
        if file_type not in ['pdf', 'docx', 'txt', 'xlsx', 'csv', 'doc', 'xls']:
            return Response(
                {'error': f'Unsupported file type: .{file_type}. Supported: pdf, docx, txt, xlsx, csv, doc, xls'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check subscription limits (graceful if subscription missing)
        subscription = getattr(request.user.organization, 'subscription', None)
        if subscription and not subscription.is_within_limits('documents'):
            return Response(
                {'error': 'Document limit exceeded'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        try:
            # Save file
            file_path = default_storage.save(f'documents/{file_obj.name}', file_obj)

            # Create document record
            document = Document.objects.create(
                user_id=request.user.id,
                title=title,
                file_type=file_type,
                file_path=file_path,
                file_size=file_obj.size
            )

            # Increment usage if subscription exists
            if subscription:
                subscription.increment_usage('documents')

            # Trigger async processing
            process_document.delay(
                document.id,
                request.user.organization.schema_name
            )

            return Response(
                DocumentSerializer(document).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error uploading document: {e}", exc_info=True)
            return Response(
                {'error': f'Failed to upload document: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentListView(generics.ListAPIView):
    """List user's documents"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user_id=self.request.user.id)


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete document"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user_id=self.request.user.id)


class PhotoUploadView(generics.CreateAPIView):
    """Upload and process photo"""
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request):
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check file type
        if not file_obj.content_type.startswith('image/'):
            return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)

        # Check subscription limits
        subscription = request.user.organization.subscription
        if not subscription.is_within_limits('photos'):
            return Response(
                {'error': 'Photo limit exceeded'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Save file
        file_path = default_storage.save(f'photos/{file_obj.name}', file_obj)

        # Create photo record
        photo = Photo.objects.create(
            user_id=request.user.id,
            file_path=file_path,
            file_size=file_obj.size
        )

        # Increment usage
        subscription.increment_usage('photos')

        # Trigger async processing
        process_photo.delay(
            photo.id,
            request.user.organization.schema_name
        )

        return Response(
            PhotoSerializer(photo).data,
            status=status.HTTP_201_CREATED
        )


class PhotoListView(generics.ListAPIView):
    """List user's photos"""
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Photo.objects.filter(user_id=self.request.user.id)
