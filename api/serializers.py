from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer

from api.models import Class, Student


User = get_user_model()


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    """
    Custom JWT serializer that enriches the generated access token
    with additional user-related claims.

    Added claims:
    - first_name
    - last_name
    - middle_name
    - email
    - phone_number
    - role
    - is_superuser
    - is_staff
    - is_active
    - created
    - updated
    """

    @classmethod
    def get_token(cls, user):
        """
        Build and return a JWT token with custom user claims.
        """

        token = super().get_token(user)

        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["middle_name"] = user.middle_name
        token["email"] = user.email
        token["phone_number"] = f"{user.phone_number}"
        token["role"] = user.role
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff
        token["is_active"] = user.is_active
        token["created"] = user.created.isoformat()
        token["updated"] = user.updated.isoformat()

        return token


class UserSerializer(ModelSerializer):
    """
    Serializer for the custom User model.

    Notes:
    - The password field is write-only and is never returned in responses.
    - On creation, the provided password is hashed before saving.
    - On update, the password is re-hashed only if a new value is provided.
    """

    class Meta:
        model = User
        exclude = ["last_login", "groups", "user_permissions"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            }
        }

    def create(self, validated_data):
        """
        Create and return a new user instance.

        Behavior:
        - If a password is provided, it is hashed via set_password().
        - If no password is provided, an unusable password is assigned.
        """

        password = validated_data.pop("password", None)
        user = User(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing user instance.

        Behavior:
        - Regular fields are assigned directly to the model instance.
        - If a new password is provided, it is hashed before saving.
        - This method is used for both full and partial updates.
        """

        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance



class SimpleStudentSerializer(ModelSerializer):
    """
    Serializer for simple student data without student_class key to add student to class's data
    """

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        """
        Remove student_class key from student's data
        """

        representation = super().to_representation(instance)

        if "student_class" in representation.keys():
            representation.pop("student_class")

        return representation


class StudentSerializer(ModelSerializer):
    """
    Serializer for the Student model.

    Output customization:
    - The serialized representation includes a nested `student_class`
      object instead of only exposing the raw relation identifier.
    """

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        """
        Convert a Student instance to a response-friendly representation.

        Adds a nested serialized representation of the related class
        under the `student_class` key.
        """

        representation = super().to_representation(instance)
        representation["student_class"] = (
            ClassSerializer(instance.student_class).data
            if instance.student_class
            else None
        )
        return representation


class ClassSerializer(ModelSerializer):
    """
    Serializer for the Class model.

    Input behavior:
    - The `teacher` field accepts a primary key value.

    Output customization:
    - The serialized representation returns the teacher as a nested
      user object instead of only exposing the raw primary key.
    """

    teacher = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Class
        fields = "__all__"

    def to_representation(self, instance):
        """
        Convert a Class instance to a response-friendly representation.

        Replaces the raw `teacher` primary key value with a nested
        serialized user object.
        """

        representation = super().to_representation(instance)
        representation["teacher"] = UserSerializer(instance.teacher).data
        representation["students"] = SimpleStudentSerializer(instance.student_set.all(), many=True).data
        return representation
