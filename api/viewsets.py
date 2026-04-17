from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet

from api.serializers import UserSerializer, StudentSerializer, ClassSerializer
from api.mixins import PaginationMixin, SearchMixin, AuthenticationMixin
from api.models import Student, Class


User = get_user_model()


class UserViewSet(PaginationMixin, SearchMixin, AuthenticationMixin, ModelViewSet):
    """
    Viewset for User model
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ["first_name", "last_name", "middle_name", "email", "phone_number"]


class StudentViewSet(PaginationMixin, SearchMixin, AuthenticationMixin, ModelViewSet):
    """
    Viewset for Studen model
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    search_fields = ["first_name", "last_name", "middle_name", "email", "phone_number"]


class ClassViewSet(PaginationMixin, SearchMixin, AuthenticationMixin, ModelViewSet):
    """
    Viewset for Class model
    """

    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    search_fields = ["name"]

