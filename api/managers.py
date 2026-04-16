from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from api.enums import UserRoles


class UserManager(BaseUserManager):
    def create_user(self, first_name: str, last_name: str, middle_name: str, phone_number: str, password: str = None, **extra_fields) -> type[AbstractUser]:
        """
        Method to create a user
        """

        if not first_name:
            raise ValidationError("User must have an first name")

        if not last_name:
            raise ValidationError("User must have an last name")

        if not middle_name:
            raise ValidationError("User must have an middle name")

        if not phone_number:
            raise ValidationError("User must have an phone number")

        if extra_fields.get("email"):
            email = self.normalize_email(email=email)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone_number=phone_number,
            **extra_fields,
        )

        user.set_password(raw_password=password)
        user.save()

        return user


    def create_superuser(self, first_name: str, last_name: str, middle_name: str, phone_number: str, password: str, **extra_fields) -> type[AbstractUser]:
        """
        Method to create a superuser
        """

        superuser = self.create_user(first_name, last_name, middle_name, phone_number, password, **extra_fields)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.role = UserRoles.SUPERUSER
        superuser.save()

        return superuser
