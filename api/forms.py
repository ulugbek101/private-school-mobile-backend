from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

from api.models import User


class CustomUserCreationForm(forms.ModelForm):
    """
    Admin form for creating users.

    Validates password confirmation and hashes the password before saving.
    """

    password1 = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Подтверждение пароля"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            "phone_number",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Пароли не совпадают."))

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class CustomUserChangeForm(forms.ModelForm):
    """
    Admin form for updating users.

    Displays the hashed password as read-only and preserves it unless
    explicitly changed through a dedicated password workflow.
    """

    password = ReadOnlyPasswordHashField(label=_("Пароль"))

    class Meta:
        model = User
        fields = (
            "phone_number",
            "password",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def clean_password(self):
        return self.initial["password"]
