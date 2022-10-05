from django import forms

# taken from cmpe321ps/django

class UserLoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(widget=forms.PasswordInput)