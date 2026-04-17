from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoles(models.TextChoices):
    """
    User roles
    """

    TEACHER = "teacher", _("Преподаватель")
    ADMIN = "admin", _("Администратор")
    SUPERUSER = "superuser", _("Суперпользователь")


class Months(models.TextChoices):
    """
    Months enum
    """

    JAN = 1, _("Январь")
    FEB = 1, _("Февраль")
    MAR = 1, _("Март")
    APR = 1, _("Апрель")
    MAY = 1, _("Май")
    JUN = 1, _("Июнь")
    JUL = 1, _("Июль")
    AUG = 1, _("Август")
    SEP = 1, _("Сентябрь")
    OCT = 1, _("Октябрь")
    NOV = 1, _("Ноябрь")
    DEC = 1, _("Декабрь")
