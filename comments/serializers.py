from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'body', 'task', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'task', 'author', 'created_at', 'updated_at']

    def get_author(self, obj):
        return {
            'id': obj.author.pk,
            'email': obj.author.email,
            'first_name': obj.author.first_name,
            'last_name': obj.author.last_name,
        }

    def validate_body(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Comment body cannot be empty.')
        return value
