from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from accounts.models import Profile, CustomUser

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']
        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.initial.get('email')
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'Email'},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data