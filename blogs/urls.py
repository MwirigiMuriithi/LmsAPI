from django.urls import path
from .views import BlogListCreateView, BlogDetailView, BlogDeleteView, CommentCreateView

urlpatterns = [
    path('blogs/', BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='blog-detail'),
    path('blogs/<int:pk>/delete/', BlogDeleteView.as_view(), name='blog-delete'),
    path('blogs/<int:blog_id>/comments/', CommentCreateView.as_view(), name='comment-create'),
]

