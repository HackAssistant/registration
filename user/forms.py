from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts

from user.models import User
from user import models


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Passwords are not stored in plaintext, so there is no way to see "
                                                    "this user's password"))

    password1 = forms.CharField(required=False, widget=forms.PasswordInput, label='Password', max_length=100)

    password2 = forms.CharField(required=False, widget=forms.PasswordInput, label='Repeat password', max_length=100,
                                help_text=' '.join(password_validators_help_texts()))

    class Meta:
        model = User
        exclude = []

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        if self.initial:
            self.fields.pop('password1')
            self.fields.pop('password2')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        if self.initial:
            return self.initial["password"]

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data.get("password2", None)
        if not self.initial and password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        validate_password(password1)
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserChangeForm, self).save(commit=False)
        if not self.initial:
            user.set_password(self.cleaned_data["password2"])
            if commit:
                user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=100)


class RegisterForm(LoginForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=100,
                                help_text=' '.join(password_validators_help_texts()))
    name = forms.CharField(label='Full name', max_length=225, help_text='What is your preferred full name?')

    field_order = ['name', 'email', 'password', 'password2']

    def __init__(self, *args, **kwargs):
        self._type = kwargs.pop('type', None)
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        validate_password(password)
        return password2

    def clean(self):
        # Check if the parameter of the url is one of our user types
        if self._type not in models.USR_URL_TYPE:
            raise forms.ValidationError("Unexpected type. Are you trying to hack us?")
        return self.cleaned_data


class RegisterSponsorForm(forms.Form):
    name = forms.CharField(label='Company name', max_length=225)
    email = forms.EmailField(label='Email', max_length=100, help_text='Can be an invented email')
    n_max = forms.IntegerField(label='Number of applications max that can create this sponsor')

    def clean_n_max(self):
        n_max = self.cleaned_data['n_max']
        if n_max < 1:
            forms.ValidationError("Set a positive number, please")
        return n_max


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "We couldn't find a user with that email address. Why not register an account?"
            )
        return email


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        strip=False,

    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput,
        help_text=' '.join(password_validation.password_validators_help_texts()),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The passwords do not match.")
        password_validation.validate_password(password2)
        return password2

    def save(self, user):
        password = self.cleaned_data["new_password1"]
        user.set_password(password)
        user.save()
