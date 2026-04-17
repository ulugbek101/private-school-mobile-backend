from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from api.enums import UserRoles


class UserManager(BaseUserManager):
    def create_user(self, first_name: str, last_name: str, middle_name: str, phone_number: str, password: str = None, **extra_fields) -> AbstractUser:
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

        # normalize email
        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone_number=phone_number,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user


    def create_superuser(self, first_name: str, last_name: str, middle_name: str, phone_number: str, password: str, **extra_fields) -> AbstractUser:
        """
        Method to create a superuser
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRoles.SUPERUSER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        user = self.create_user(
            first_name,
            last_name,
            middle_name,
            phone_number,
            password,
            **extra_fields
        )

        return user
