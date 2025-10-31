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
