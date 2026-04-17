from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from api.models import Class, Student, Payment, Expense, ExpenseCategory
from api.forms import CustomUserCreationForm, CustomUserChangeForm


User = get_user_model()


admin.site.unregister(Group)
admin.site.site_header = _("Администрирование системы школы")
admin.site.site_title = _("Панель администратора")
admin.site.index_title = _("Панель управления")


class StudentInline(admin.TabularInline):
    """
    Inline representation of students belonging to a class.

    This inline is read-optimized and keeps the class page concise while
    still allowing quick navigation through enrolled students.
    """

    model = Student
    extra = 0
    fields = ("first_name", "last_name", "middle_name", "phone_number", "email", "created")
    readonly_fields = ("created",)
    show_change_link = True


class PaymentInline(admin.TabularInline):
    """
    Inline representation of student payments.

    Useful inside Student admin to inspect a student's payment history
    without leaving the student detail page.
    """

    model = Payment
    extra = 0
    fields = ("class_object", "amount", "month", "created_by", "created")
    readonly_fields = ("created",)
    show_change_link = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administrative configuration for the custom User model.

    Key features:
    - supports Django's password hashing workflow through BaseUserAdmin;
    - provides structured field grouping for identity and permissions;
    - exposes search and filtering over operational user fields;
    - keeps audit timestamps read-only.
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
        "phone_number",
        "email",
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "created",
    )
    list_display_links = ("id", "first_name", "last_name")
    list_filter = (
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "created",
        "updated",
    )
    search_fields = (
        "first_name",
        "last_name",
        "middle_name",
        "email",
        "phone_number",
    )
    ordering = ("-created",)
    readonly_fields = ("created", "updated", "last_login")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (
            _("Аутентификация"),
            {
                "fields": ("phone_number", "password"),
            },
        ),
        (
            _("Личная информация"),
            {
                "fields": ("first_name", "last_name", "middle_name", "email", "role"),
            },
        ),
        (
            _("Права и доступ"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("last_login", "created", "updated"),
            },
        ),
    )

    add_fieldsets = (
        (
            _("Создание пользователя"),
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "email",
                    "role",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """
    Administrative configuration for academic classes.

    Key features:
    - optimized teacher selection;
    - inline visibility of enrolled students;
    - filtering and searching by class name and teacher identity.
    """

    list_display = ("id", "name", "teacher", "students_count", "created", "updated")
    list_display_links = ("id", "name")
    list_filter = ("teacher", "created", "updated")
    search_fields = (
        "name",
        "teacher__first_name",
        "teacher__last_name",
        "teacher__middle_name",
        "teacher__phone_number",
        "teacher__email",
    )
    ordering = ("-created",)
    readonly_fields = ("created", "updated")
    autocomplete_fields = ("teacher",)
    inlines = [StudentInline]

    fieldsets = (
        (
            _("Информация о классе"),
            {
                "fields": ("name", "teacher"),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created", "updated"),
            },
        ),
    )

    @admin.display(description=_("Количество учеников"))
    def students_count(self, obj):
        return obj.student_set.count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Administrative configuration for students.

    Key features:
    - supports filtering by class and timestamps;
    - enables searching by identity and contact fields;
    - displays related class directly in the list view;
    - exposes related payments inline for operational review.
    """

    list_display = (
        "id",
        "first_name",
        "last_name",
        "middle_name",
        "phone_number",
        "email",
        "student_class",
        "birthday",
        "created",
    )
    list_display_links = ("id", "first_name", "last_name")
    list_filter = ("student_class", "birthday", "created", "updated")
    search_fields = (
        "first_name",
        "last_name",
        "middle_name",
        "email",
        "phone_number",
        "student_class__name",
    )
    ordering = ("-created",)
    readonly_fields = ("created", "updated")
    autocomplete_fields = ("student_class",)
    inlines = [PaymentInline]

    fieldsets = (
        (
            _("Информация об ученике"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "middle_name",
                    "birthday",
                    "email",
                    "phone_number",
                    "student_class",
                ),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created", "updated"),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Administrative configuration for payment records.

    Key features:
    - displays operational and historical snapshot fields together;
    - supports filtering by month, class, staff member, and timestamps;
    - keeps snapshot fields read-only to preserve audit integrity.

    Snapshot fields:
    - `_student`
    - `_class_object`
    - `_created_by`

    These fields are intended to preserve historical readability after
    related objects are deleted.
    """

    list_display = (
        "id",
        "student_display",
        "class_display",
        "amount",
        "month",
        "created_by_display",
        "created",
    )
    list_display_links = ("id",)
    list_filter = ("month", "class_object", "created_by", "created", "updated")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__middle_name",
        "_student",
        "class_object__name",
        "_class_object",
        "created_by__first_name",
        "created_by__last_name",
        "created_by__middle_name",
        "_created_by",
    )
    ordering = ("-created",)
    readonly_fields = (
        "_student",
        "_class_object",
        "_created_by",
        "created",
        "updated",
    )
    autocomplete_fields = ("student", "class_object", "created_by")

    fieldsets = (
        (
            _("Актуальные связи"),
            {
                "fields": ("student", "class_object", "created_by"),
            },
        ),
        (
            _("Данные оплаты"),
            {
                "fields": ("amount", "month"),
            },
        ),
        (
            _("Исторические снимки"),
            {
                "fields": ("_student", "_class_object", "_created_by"),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created", "updated"),
            },
        ),
    )

    @admin.display(description=_("Ученик"))
    def student_display(self, obj):
        return obj.student.fullname if obj.student else obj._student

    @admin.display(description=_("Класс"))
    def class_display(self, obj):
        return obj.class_object.name if obj.class_object else obj._class_object

    @admin.display(description=_("Кем создано"))
    def created_by_display(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else obj._created_by


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """
    Administrative configuration for expense categories.
    """

    list_display = ("id", "name", "created", "updated")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("-created",)
    readonly_fields = ("created", "updated")

    fieldsets = (
        (
            _("Информация о категории"),
            {
                "fields": ("name",),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created", "updated"),
            },
        ),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """
    Administrative configuration for expense transactions.

    Key features:
    - supports operational filtering by category and creator;
    - exposes snapshot fields for historical continuity;
    - protects snapshot values from accidental manual editing.
    """

    list_display = (
        "id",
        "amount",
        "category_display",
        "created_by_display",
        "created",
    )
    list_display_links = ("id",)
    list_filter = ("category", "created_by", "created", "updated")
    search_fields = (
        "description",
        "category__name",
        "_category",
        "created_by__first_name",
        "created_by__last_name",
        "created_by__middle_name",
        "_created_by",
    )
    ordering = ("-created",)
    readonly_fields = (
        "_category",
        "_created_by",
        "created",
        "updated",
    )
    autocomplete_fields = ("category", "created_by")

    fieldsets = (
        (
            _("Данные затраты"),
            {
                "fields": ("category", "amount", "description", "created_by"),
            },
        ),
        (
            _("Исторические снимки"),
            {
                "fields": ("_category", "_created_by"),
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("created", "updated"),
            },
        ),
    )

    @admin.display(description=_("Категория"))
    def category_display(self, obj):
        return obj.category.name if obj.category else obj._category

    @admin.display(description=_("Кем создано"))
    def created_by_display(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else obj._created_by
