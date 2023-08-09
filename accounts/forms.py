from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email",)

    def clean_password2(self):
        cd = self.cleaned_data
        pw1 = cd.get("password1")
        pw2 = cd.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise ValidationError("Passwords must match.")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.changed_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "phone_number",
            "is_active",
            "is_admin",
            "is_superuser",
        )


class UserRegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_confirm_password(self):
        cd = self.cleaned_data
        if (
            cd["confirm_password"] != cd["password"]
            and cd["password"]
            and cd["confirm_password"]
        ):
            raise ValidationError("Passwords must match.")
        return cd["confirm_password"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email already exists.")
        return email


class VerifyForm(forms.Form):
    code = forms.IntegerField(min_value=1000, max_value=9999)


class LoginForm(forms.Form):
    email = forms.CharField(label="Username/Email")
    password = forms.CharField(widget=forms.PasswordInput)


class ChangeUsernameForm(forms.Form):
    username = forms.CharField(max_length=255)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username already exists.")
        return username
