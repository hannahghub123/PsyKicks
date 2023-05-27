from django import forms

class SignupForm(forms.Form):
    username = forms.CharField(max_length=10)
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phonenumber = forms.CharField(max_length=10)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
