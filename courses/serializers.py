from rest_framework import serializers
from .models import Course, Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ('student', 'course', 'enrolled_at')

class CourseSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = ('id', 'instructor', 'title', 'description', 'created_at', 'updated_at', 'enrollments')
