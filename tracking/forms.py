from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=150)


def custom_password_validator(value):
    if len(value) < 8:
        raise ValidationError("The password must has more the 8 characters")
    return value


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        validators=[custom_password_validator],
        help_text="Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
