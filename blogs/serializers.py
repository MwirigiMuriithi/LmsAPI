from rest_framework import serializers
from .models import Blog, Comment, Like

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at')

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'blog', 'created_at')

class BlogSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ('id', 'author', 'title', 'content', 'created_at', 'comments')
    def get_likes_count(self, obj):
        return obj.likes.count()
    