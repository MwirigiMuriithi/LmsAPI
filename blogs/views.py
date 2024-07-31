from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Blog, Comment, Like
from .serializers import BlogSerializer, CommentSerializer, LikeSerializer

from accounts.permissions import IsAuthenticatedAndActive
from .permissions import IsAuthorOrSuperuser

class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class BlogDetailView(generics.RetrieveAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

class BlogDeleteView(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedAndActive, IsAuthorOrSuperuser]
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def perform_create(self, serializer):
        blog = Blog.objects.get(pk=self.kwargs['blog_id'])
        serializer.save(blog=blog, author=self.request.user)

class BlogLikeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, *args, **kwargs):
        blog = Blog.objects.get(pk=self.kwargs['pk'])
        user = request.user
        # Check if the user has already liked this blog
        if Like.objects.filter(user=user, blog=blog).exists():
            return Response({'detail': 'You have already liked this blog'}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=user, blog=blog)
        return Response({'detail': 'Blog liked'}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        blog = Blog.objects.get(pk=self.kwargs['pk'])
        user = request.user
        # Check if the user has liked this blog
        like = Like.objects.filter(user=user, blog=blog).first()
        if not like:
            return Response({'detail': 'Like not found'}, status=status.HTTP_404_NOT_FOUND)
        like.delete()
        return Response({'detail': 'Blog unliked'}, status=status.HTTP_204_NO_CONTENT)    