# Module: forms.py

# Import Neccessary Libaries
from django import forms
from django.contrib.auth.models import User

# Get details from user 
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    enrollment_number = forms.CharField(required=True, max_length=50)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(required=True,max_length=100)
    phone = forms.CharField(required=False, max_length=20)
    education = forms.CharField(required=True,max_length=30)



    class Meta:
        model = User
        fields = ['username', 'email','first_name', 'last_name', 'enrollment_number', 'phone','address',"education"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data









    
  



