from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from api.enums import UserRoles
from api.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Core User model for system
    """

    first_name = models.CharField(verbose_name=_("Имя"), max_length=50)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50)
    middle_name = models.CharField(verbose_name=_("Отчество"), max_length=50)
    email = models.EmailField(verbose_name=_("E-mail адрес"), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_("Номер телефона"), unique=True)
    role = models.CharField(verbose_name=_("Статус сотрудника"), choices=UserRoles.choices)
    is_superuser = models.BooleanField(verbose_name=_("Статус суперпользователя"), help_text=_("Самое высокое звание. Для такого типа пользователя ограничений - нет"), default=False)
    is_staff = models.BooleanField(verbose_name=_("Статус сотрудника"), help_text=_("Может ли пользователь входить в админ панель"), default=False)
    is_active = models.BooleanField(verbose_name=_("Статус активности"), help_text=_("Вместо того, что бы удалять аккаунт - просто выключите этот индикатор"), default=True)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name", "email"]
    USERNAME_FIELD = "phone_number"

    def get_username(self):
        return self.__str__()

    def get_full_name(self):
        return self.__str__()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        unique_together = ["first_name", "last_name", "middle_name"]
