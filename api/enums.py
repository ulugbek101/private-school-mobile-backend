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

    JAN = "1", _("Январь")
    FEB = "2", _("Февраль")
    MAR = "3", _("Март")
    APR = "4", _("Апрель")
    MAY = "5", _("Май")
    JUN = "6", _("Июнь")
    JUL = "7", _("Июль")
    AUG = "8", _("Август")
    SEP = "9", _("Сентябрь")
    OCT = "10", _("Октябрь")
    NOV = "11", _("Ноябрь")
    DEC = "12", _("Декабрь")
