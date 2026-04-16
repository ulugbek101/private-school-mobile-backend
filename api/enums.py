from django.db import models


class UserRoles(models.TextChoices):
    """
    User roles
    """

    TEACHER = "teacher", "Ustoz"
    ADMIN = "admin", "Admin"
    SUPERUSER = "superuser", "Superadmin"
