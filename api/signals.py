from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

from api.models import User, Student, Class, Payment, ExpenseCategory, Expense


def build_person_full_name(instance) -> str:
    """
    Build a safe human-readable full name for a person-like object.

    The function ignores empty name parts and joins only existing values.
    This avoids strings such as 'John Doe None'.
    """
    parts = [instance.first_name, instance.last_name, instance.middle_name]
    return " ".join(str(part).strip() for part in parts if part)


@receiver(pre_save, sender=Payment)
def fill_payment_snapshot_fields(sender, instance: Payment, **kwargs):
    """
    Synchronize snapshot fields for Payment before the model is saved.

    Purpose:
    - preserves printable values for related entities;
    - ensures receipt/report data remains available even if related
      objects are later deleted.

    Behavior:
    - if `student` is set, `_student` is filled from the current student name;
    - if `class_object` is set, `_class_object` is filled from the current class name;
    - if `created_by` is set, `_created_by` is filled from the current staff full name.
    """
    if instance.student:
        instance._student = build_person_full_name(instance.student)

    if instance.class_object:
        instance._class_object = instance.class_object.name

    if instance.created_by:
        instance._created_by = build_person_full_name(instance.created_by)


@receiver(pre_save, sender=Expense)
def fill_expense_snapshot_fields(sender, instance: Expense, **kwargs):
    """
    Synchronize snapshot fields for Expense before the model is saved.

    Purpose:
    - preserves human-readable values for related entities;
    - ensures expense history remains readable after related-object deletion.

    Behavior:
    - if `category` is set, `_category` is filled from the current category name;
    - if `created_by` is set, `_created_by` is filled from the current staff full name.
    """
    if instance.category:
        instance._category = instance.category.name

    if instance.created_by:
        instance._created_by = build_person_full_name(instance.created_by)


@receiver(pre_delete, sender=Student)
def snapshot_student_before_delete(sender, instance: Student, **kwargs):
    """
    Preserve student snapshot data in related Payment records before
    the Student object is deleted.

    Why this is necessary:
    - `Payment.student` uses `on_delete=SET_NULL`;
    - after deletion, the foreign key will become NULL;
    - this signal stores the student's printable name in `_student`
      before that happens.
    """
    student_name = build_person_full_name(instance)
    Payment.objects.filter(student=instance).update(_student=student_name)


@receiver(pre_delete, sender=Class)
def snapshot_class_before_delete(sender, instance: Class, **kwargs):
    """
    Preserve class snapshot data in related Payment records before
    the Class object is deleted.

    Why this is necessary:
    - `Payment.class_object` uses `on_delete=SET_NULL`;
    - after deletion, the foreign key will become NULL;
    - this signal stores the class name in `_class_object` first.
    """
    Payment.objects.filter(class_object=instance).update(_class_object=instance.name)


@receiver(pre_delete, sender=User)
def snapshot_user_before_delete(sender, instance: User, **kwargs):
    """
    Preserve staff snapshot data in related Payment and Expense records
    before the User object is deleted.

    Why this is necessary:
    - `created_by` in both models uses `on_delete=SET_NULL`;
    - after deletion, the foreign key will become NULL;
    - this signal stores the user's full name in snapshot fields first.

    Notes:
    - this signal only affects historical/audit fields in Payment and Expense;
    - it does not affect relations protected with `on_delete=PROTECT`
      such as `Class.teacher`.
    """
    user_full_name = build_person_full_name(instance)

    Payment.objects.filter(created_by=instance).update(_created_by=user_full_name)
    Expense.objects.filter(created_by=instance).update(_created_by=user_full_name)


@receiver(pre_delete, sender=ExpenseCategory)
def snapshot_category_before_delete(sender, instance: ExpenseCategory, **kwargs):
    """
    Preserve category snapshot data in related Expense records before
    the ExpenseCategory object is deleted.

    Why this is necessary:
    - `Expense.category` uses `on_delete=SET_NULL`;
    - after deletion, the foreign key will become NULL;
    - this signal stores the category name in `_category` first.
    """
    Expense.objects.filter(category=instance).update(_category=instance.name)
