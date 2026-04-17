from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.serializers import ModelSerializer

from api.models import Class, Student


User = get_user_model()


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['middle_name'] = user.middle_name
        token['email'] = user.email
        token['phone_number'] = f'{user.phone_number}'
        token['role'] = user.role
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        token['is_active'] = user.is_active
        token['created'] = user.created.isoformat()
        token['updated'] = user.updated.isoformat()

        return token


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class StudentSerializer(ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class ClassSerializer(ModelSerializer):
    teacher = UserSerializer(many=False)
    students = StudentSerializer(many=True)

    class Meta:
        model = Class
        fields = "__all__"
