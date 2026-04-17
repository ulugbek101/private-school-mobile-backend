from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from api.enums import UserRoles, Months
from api.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Application user model used for authentication and staff access control.

    This model uses `phone_number` as the unique authentication identifier
    (`USERNAME_FIELD`) instead of the default username field.

    Functional responsibilities:
    - stores personal identity fields;
    - stores role and permission-related flags;
    - supports Django authentication through AbstractBaseUser;
    - supports groups and permissions through PermissionsMixin.

    Notes:
    - password hashing should be handled by the custom manager, serializers,
      or admin forms, not inside `save()`;
    - `is_staff` controls access to the Django admin panel;
    - `is_superuser` grants unrestricted permission checks.
    """

    first_name = models.CharField(verbose_name=_("Имя"), max_length=50)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50)
    middle_name = models.CharField(
        verbose_name=_("Отчество"),
        max_length=50,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("E-mail адрес"),
        null=True,
        blank=True,
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Номер телефона"),
        unique=True,
    )
    role = models.CharField(
        verbose_name=_("Статус сотрудника"),
        choices=UserRoles.choices,
    )
    is_superuser = models.BooleanField(
        verbose_name=_("Статус суперпользователя"),
        help_text=_("Самое высокое звание. Для такого типа пользователя ограничений - нет"),
        default=False,
    )
    is_staff = models.BooleanField(
        verbose_name=_("Статус сотрудника"),
        help_text=_("Может ли пользователь входить в админ панель"),
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name=_("Статус активности"),
        help_text=_("Вместо того, что бы удалять аккаунт - просто выключите этот индикатор"),
        default=True,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name", "email"]

    def get_username(self):
        """
        Return the human-readable identifier for the authenticated user.
        """
        return self.__str__()

    def get_full_name(self):
        """
        Return the full display name of the user.
        """
        return self.__str__()

    def __str__(self):
        """
        Return the full name representation of the user.
        """
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        unique_together = ["first_name", "last_name", "middle_name"]


class Student(models.Model):
    """
    Student entity associated with a single academic class.

    Functional responsibilities:
    - stores student identity and contact fields;
    - stores optional birthday information;
    - links each student to exactly one `Class`;
    - exposes a computed `fullname` property for display purposes.

    Deletion policy:
    - related class deletion is protected with `on_delete=models.PROTECT`,
      so a class cannot be removed while students still reference it.
    """

    first_name = models.CharField(verbose_name=_("Имя"), max_length=50)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50)
    middle_name = models.CharField(
        verbose_name=_("Отчество"),
        max_length=50,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_("E-mail адрес"),
        null=True,
        blank=True,
    )
    birthday = models.DateField(
        verbose_name=_("День рождения"),
        null=True,
        blank=True,
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Номер телефона"),
        unique=True,
    )
    student_class = models.ForeignKey(
        verbose_name=_("Класс студента"),
        to="Class",
        on_delete=models.PROTECT,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    @property
    def fullname(self):
        """
        Return the full display name of the student.
        """
        return self.__str__()

    def __str__(self):
        """
        Return the full name representation of the student.
        """
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Студент")
        verbose_name_plural = _("Студенты")
        unique_together = ["first_name", "last_name", "middle_name"]


class Class(models.Model):
    """
    Academic class entity.

    Functional responsibilities:
    - stores the class name;
    - links the class to a responsible teacher;
    - acts as the parent academic grouping for students.

    Deletion policy:
    - teacher deletion is protected with `on_delete=models.PROTECT`,
      so a teacher referenced by a class cannot be deleted until the
      relation is reassigned or removed.
    """

    name = models.CharField(
        verbose_name=_("Название класса"),
        max_length=50,
        unique=True,
    )
    teacher = models.ForeignKey(
        verbose_name=_("Преподаватель"),
        to=User,
        help_text=_("Кто будет преподавать этому классу"),
        on_delete=models.PROTECT,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    def __str__(self):
        """
        Return the class name.
        """
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Класс")
        verbose_name_plural = _("Классы")


class Payment(models.Model):
    """
    Payment record for a student's tuition or class-related payment.

    Functional responsibilities:
    - stores the student, class, amount, and payment month;
    - stores the employee who registered the payment;
    - preserves textual snapshots of related entities in underscore-prefixed
      fields so receipt/audit data can survive related-object deletion.

    Snapshot fields:
    - `_student`
    - `_class_object`
    - `_created_by`

    These fields are intended to retain printable or historical information
    after related objects are deleted, but they must be populated by explicit
    application logic.
    """

    student = models.ForeignKey(
        verbose_name=_("Студент"),
        to=Student,
        on_delete=models.SET_NULL,
        null=True,
    )
    _student = models.CharField(
        verbose_name=_("ФИО удаленного студента"),
        help_text=_("Поле заполнится автоматически при удалении студента, для сохранения данных студента - для вывода чека"),
        null=True,
        blank=True,
    )
    class_object = models.ForeignKey(
        verbose_name=_("Класс"),
        to=Class,
        on_delete=models.SET_NULL,
        null=True,
    )
    _class_object = models.CharField(
        verbose_name=_("Наименование удаленного класса"),
        help_text=_("Поле заполнится автоматически при удалении класса, для сохранения данных класса - для вывода чека"),
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        verbose_name=_("Сумма"),
        max_digits=12,
        decimal_places=2,
    )
    month = models.CharField(
        verbose_name=_("Месяц, для которого заносится оплата"),
        choices=Months,
        max_length=20,
    )
    created_by = models.ForeignKey(
        verbose_name=_("Сотрудник, занесший оплату в систему"),
        to=User,
        on_delete=models.SET_NULL,
        null=True,
    )
    _created_by = models.CharField(
        verbose_name=_("ФИО сотрудника, занесший оплату в систему"),
        help_text=_("Поле заполнится автоматически при удалении сотрудника, для сохранения данных этого сотрудника - для вывода чека"),
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    def __str__(self):
        """
        Return a concise human-readable payment description.
        """
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
    Reference model representing an expense classification.

    Typical examples:
    - rent;
    - utilities;
    - salaries;
    - school supplies.
    """

    name = models.CharField(
        verbose_name=_("Название затраты"),
        max_length=100,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    def __str__(self):
        """
        Return the expense category name.
        """
        return self.name

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Тип затраты")
        verbose_name_plural = _("Типы затрат")


class Expense(models.Model):
    """
    Expense transaction recorded by the organization.

    Functional responsibilities:
    - stores the expense category, amount, and optional description;
    - stores the staff member who registered the expense;
    - preserves textual snapshots of deleted related objects in underscore-
      prefixed fields for historical reporting and receipt generation.

    Snapshot fields:
    - `_category`
    - `_created_by`
    """

    category = models.ForeignKey(
        verbose_name=_("Категория затраты"),
        to=ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
    )
    _category = models.CharField(
        verbose_name=_("Наименование категории затраты"),
        help_text=_("Это поле заполнится автоматически при удалении категории затраты"),
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        verbose_name=_("Сумма"),
        max_digits=12,
        decimal_places=2,
    )
    description = models.TextField(
        verbose_name=_("Описание затраты"),
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        verbose_name=_("Сотрудник, занесший затрату в систему"),
        to=User,
        on_delete=models.SET_NULL,
        null=True,
    )
    _created_by = models.CharField(
        verbose_name=_("ФИО сотрудника, занесший затрату в систему"),
        help_text=_("Поле заполнится автоматически при удалении сотрудника, для сохранения данных этого сотрудника - для вывода чека"),
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        verbose_name=_("Дата создания"),
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name=_("Дата обновления"),
        auto_now=True,
    )

    def __str__(self):
        """
        Return a concise human-readable expense description.
        """
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
