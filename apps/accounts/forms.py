from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

INPUT_CLASS = 'fin-input'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Email ou nom d\'utilisateur', 'class': INPUT_CLASS})
        self.fields['password'].widget.attrs.update({'placeholder': '••••••••', 'class': INPUT_CLASS})


class RegisterForm(UserCreationForm):
    first_name  = forms.CharField(label='Prénom', max_length=100)
    last_name   = forms.CharField(label='Nom', max_length=100)
    email       = forms.EmailField(label='Email')
    profession  = forms.CharField(label='Profession', max_length=200, required=False)
    city        = forms.CharField(label='Ville', max_length=100, initial='Yaoundé')

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'profession', 'city', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = INPUT_CLASS


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email', 'phone',
                  'city', 'country', 'profession', 'monthly_income_target', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = INPUT_CLASS
