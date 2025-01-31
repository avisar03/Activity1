from django import forms
from django.contrib.auth.hashers import make_password
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input'}),
        label="Confirm Password"
    )

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email', 'address', 'phone_number', 'birth_date', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'input', 'type': 'password'}),
            'birth_date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': 'input'})
        self.fields['last_name'].widget.attrs.update({'class': 'input'})
        self.fields['email'].widget.attrs.update({'class': 'input', 'type': 'email'})
        self.fields['address'].widget.attrs.update({'class': 'input'})
        self.fields['phone_number'].widget.attrs.update({'class': 'input'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Hash the password here
        if commit:
            user.save()
        return user
    
