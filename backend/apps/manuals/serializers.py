from rest_framework import serializers
from .models import ManualCategory, Manual, ManualAttachment, ManualFeedback


class ManualCategorySerializer(serializers.ModelSerializer):
    manuals_count = serializers.SerializerMethodField()

    class Meta:
        model = ManualCategory
        fields = ['id', 'name', 'slug', 'icon', 'order', 'manuals_count']

    def get_manuals_count(self, obj):
        return obj.manuals.filter(is_published=True).count()


class ManualAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualAttachment
        fields = ['id', 'title', 'file_path', 'file_type', 'file_size', 'order']


class ManualSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    attachments = ManualAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Manual
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'category',
            'category_name',
            'integration_type',
            'content',
            'video_url',
            'video_thumbnail',
            'language',
            'order',
            'is_featured',
            'tags',
            'attachments',
            'views_count',
            'helpful_count',
            'created_at',
            'updated_at',
            'published_at'
        ]


class ManualFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualFeedback
        fields = ['id', 'manual', 'user_id', 'is_helpful', 'comment', 'created_at']
        read_only_fields = ['user_id', 'created_at']
