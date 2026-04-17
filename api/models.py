from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from api.enums import UserRoles, Months
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


class Student(models.Model):
    """
    Model to represent a Student object
    """

    first_name = models.CharField(verbose_name=_("Имя"), max_length=50)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50)
    middle_name = models.CharField(verbose_name=_("Отчество"), max_length=50)
    email = models.EmailField(verbose_name=_("E-mail адрес"), null=True, blank=True)
    born_year = models.IntegerField(verbose_name=_("Год рождения"), null=True, blank=True)
    phone_number = PhoneNumberField(verbose_name=_("Номер телефона"), unique=True)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    @property
    def fullname(self):
        return self.__str__()

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Студент")
        verbose_name_plural = _("Студенты")
        unique_together = ["first_name", "last_name", "middle_name"]


class Class(models.Model):
    """
    Model to represent a Class object
    """

    name = models.CharField(verbose_name=_("Название класса"), max_length=50, unique=True)
    teacher = models.ForeignKey(verbose_name=_("Преподаватель"), to=User, help_text=_("Кто будет преподавать этому классу"), on_delete=models.PROTECT)
    students = models.ManyToManyField(verbose_name=_("Студенты"), to=Student)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Класс")
        verbose_name_plural = _("Классы")


class Payment(models.Model):
    """
    Model to represent Student payment made for a certain Class for a certain month of a certain year
    """

    student = models.ForeignKey(verbose_name=_("Студент"), to=Student, on_delete=models.SET_NULL)
    _student = models.CharField(verbose_name=_("ФИО удаленного студента"), help_text=_("Поле заполнится автоматически при удалении студента, для сохранения данных студента - для вывода чека"), null=True, blank=True)
    class_object = models.ForeignKey(verbose_name=_("Класс"), to=Class, on_delete=models.SET_NULL)
    _class_object = models.CharField(verbose_name=_("Наименование удаленного класса"), help_text=_("Поле заполнится автоматически при удалении класса, для сохранения данных класса - для вывода чека"), null=True, blank=True)
    amount = models.DecimalField(verbose_name=_("Сумма"), max_digits=12, decimal_places=2)
    month = models.CharField(verbose_name=_("Месяц, для которого заносится оплата"), choices=Months)
    created_by = models.ForeignKey(verbose_name=_("Сотрудник, занесший оплату в систему"), to=User, on_delete=models.SET_NULL)
    _created_by = models.CharField(verbose_name=_("ФИО сотрудника, занесший оплату в систему"), help_text=_("Поле заполнится автоматически при удалении сотрудника, для сохранения данных этого сотрудника - для вывода чека"), null=True, blank=True)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    def __str__(self):
        student_name = self._student
        if self.student:
            student_name = self.student.fullname

        return f"{student_name} - {self.get_month_display()} - {self.amount}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Оплата")
        verbose_name_plural = _("Оплаты")


class ExpenseCategory(models.Model):
    """
    Model to represent the type of expense
    """

    name = models.CharField(verbose_name=_("Название затраты"), max_length=100)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Тип затраты")
        verbose_name_plural = _("Типы затрат")


class Expense(models.Model):
    """
    Model to represent the expense itself, made by organization
    """

    category = models.ForeignKey(verbose_name=_("Категория затраты"), to=ExpenseCategory, on_delete=models.SET_NULL)
    _category = models.ForeignKey(verbose_name=_("Наименование категории затраты"), help_text=_("Это поле заполнится автоматически при удалении категории затраты"), null=True, blank=True)
    amount = models.DecimalField(verbose_name=_("Сумма"), max_digits=12, decimal_places=2)
    description = models.TextField(verbose_name=_("Описание затраты"), null=True, blank=True)
    created_by = models.ForeignKey(verbose_name=_("Сотрудник, занесший затрату в систему"), to=User, on_delete=models.SET_NULL)
    _created_by = models.CharField(verbose_name=_("ФИО сотрудника, занесший затрату в систему"), help_text=_("Поле заполнится автоматически при удалении сотрудника, для сохранения данных этого сотрудника - для вывода чека"), null=True, blank=True)
    created = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("Дата обновления"), auto_now=True)

    def __str__(self):
        category_name = self._category
        if self.category:
            category_name = self.category.name

        created_staff = self._created_by
        if self.created_by:
            created_staff = self.created_by.get_full_name()

        return f"{self.amount} - {category_name} - {created_staff} - {self.created}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Затрата")
        verbose_name_plural = _("Затраты")
