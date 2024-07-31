from django.urls import path
from .views import CourseListCreateView, CourseDetailView, EnrollmentCreateView, EnrollmentListView

urlpatterns = [
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/enrollments/', EnrollmentCreateView.as_view(), name='enrollment-create'),
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment-list'),
]
