from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class NewUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model =User
        fields = ['username','email','password1','password2']

class CustomAuthenticationForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email', max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if not username_or_email or not password:
            raise forms.ValidationError("Both fields are required.")

        # Determine if the input is an email or username
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password")
        else:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid username or password")

        # Authenticate the user
        self.user_cache = authenticate(username=user.username, password=password)
        if self.user_cache is None:
            raise forms.ValidationError("Invalid username/email or password")

        return cleaned_data

    def get_user(self):
        return self.user_cache

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)