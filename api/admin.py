from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from api.models import Class, Student, Payment, Expense, ExpenseCategory

User = get_user_model()

admin.site.unregister(Group)
admin.site.register(User)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Payment)
admin.site.register(Expense)
admin.site.register(ExpenseCategory)
