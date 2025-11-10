from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import VectorStore
from .tasks import search_similar, rebuild_vector_store
from rest_framework import serializers


class VectorStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorStore
        fields = [
            'id', 'name', 'description', 'embedding_model',
            'chunk_size', 'chunk_overlap', 'total_embeddings',
            'last_updated', 'created_at'
        ]


class VectorStoreView(generics.RetrieveUpdateAPIView):
    """Get/Update vector store settings"""
    serializer_class = VectorStoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Get or create default vector store
        vector_store, _ = VectorStore.objects.get_or_create(
            id=1,
            defaults={'name': 'Default Vector Store'}
        )
        return vector_store


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def search_view(request):
    """Search for similar content"""
    query = request.data.get('query')
    limit = request.data.get('limit', 5)

    if not query:
        return Response({'error': 'Query is required'}, status=400)

    results = search_similar(
        query_text=query,
        tenant_schema=request.user.organization.schema_name,
        limit=limit
    )

    return Response({'results': results})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rebuild_view(request):
    """Rebuild entire vector store"""
    rebuild_vector_store.delay(
        tenant_schema=request.user.organization.schema_name
    )

    return Response({'message': 'Vector store rebuild initiated'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_all_view(request):
    """
    Process all unprocessed documents and photos to create embeddings
    This is the "Start Training" endpoint
    """
    from apps.documents.models import Document, Photo
    from apps.documents.tasks import process_document, process_photo
    
    tenant_schema = request.user.organization.schema_name
    
    # Process all unprocessed documents
    unprocessed_docs = Document.objects.filter(
        user_id=request.user.id,
        is_processed=False
    )
    
    for doc in unprocessed_docs:
        process_document.delay(doc.id, tenant_schema)
    
    # Process all unprocessed photos
    unprocessed_photos = Photo.objects.filter(
        user_id=request.user.id,
        is_processed=False
    )
    
    for photo in unprocessed_photos:
        process_photo.delay(photo.id, tenant_schema)
    
    return Response({
        'message': 'Processing started',
        'documents': unprocessed_docs.count(),
        'photos': unprocessed_photos.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def status_view(request):
    """
    Get training/processing status
    """
    from apps.documents.models import Document, Photo
    
    # Count processing status
    docs = Document.objects.filter(user_id=request.user.id)
    photos = Photo.objects.filter(user_id=request.user.id)
    
    total = docs.count() + photos.count()
    processed = docs.filter(is_processed=True).count() + photos.filter(is_processed=True).count()
    processing = docs.filter(processing_status='processing').count() + photos.filter(processing_status='processing').count()
    
    status = 'completed' if total > 0 and processed == total else ('processing' if processing > 0 else 'idle')
    
    return Response({
        'status': status,
        'total': total,
        'processed': processed,
        'processing': processing,
        'pending': total - processed - processing
    })
