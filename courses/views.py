from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from accounts.permissions import IsAuthenticatedAndActive

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def perform_update(self, serializer):
        # Ensure that only the instructor or a superuser can update the course
        if self.request.user != self.get_object().instructor and not self.request.user.is_superuser:
            raise permissions.PermissionDenied("You do not have permission to edit this course.")
        serializer.save()

class EnrollmentCreateView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs['course_id'])
        if Enrollment.objects.filter(student=self.request.user, course=course).exists():
            raise permissions.PermissionDenied("You are already enrolled in this course.")
        serializer.save(student=self.request.user, course=course)

class EnrollmentListView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticatedAndActive]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
