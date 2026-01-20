from django import forms
from django.contrib.auth import get_user_model 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
import re

User = get_user_model() 

alpha_only = RegexValidator(r'^[a-zA-Z]*$', 'Only letters are allowed (no numbers or symbols).')

# Validator: Letters and Spaces - For Last Name
alpha_space = RegexValidator(r'^[a-zA-Z\s]*$', 'Only letters and spaces are allowed.')

# username_regex = RegexValidator(
#     r'^[a-zA-Z0-9_]*$', 
#     'Username can only contain letters, numbers, and underscores.'
# )

def username_regex(value):
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError('Username can only contain letters, numbers, and underscores.')

def validate_password_complexity(value):
    if len(value) < 8 or len(value) > 32:
        raise ValidationError("Password must be between 8 and 32 characters.")
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', value):
        raise ValidationError("Password must contain at least one digit.")

class SignUpForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
        required=True
    )
    
    username = forms.CharField(
        validators=[username_regex, MinLengthValidator(6)],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username', 'id': 'id_username'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address', 'id': 'id_email'})
    )

    password1 = forms.CharField(
        validators=[validate_password_complexity, MinLengthValidator(8)],
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': 'Password',
            'id': 'passwordInput' # <--- MATCHES JS BELOW
        })
    )

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1']

    # --- CLEANING ---

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name')
        if name:
            # Check for digits in the name
            if any(char.isdigit() for char in name):
                raise ValidationError("Name cannot contain numbers.")
            if len(name) < 2:
                raise ValidationError("Name is too short.")
        return name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            if User.objects.filter(username=username).exists():
                raise ValidationError("This username is already taken.")
            return username
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError("This email is already registered.")
            return email
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if self.cleaned_data.get('full_name'):
            names = self.cleaned_data['full_name'].split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
                
        if commit:
            user.save()
        return user
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username or Email", # Changed label
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email', # Changed placeholder
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'passwordInput', 
        })
    )

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        validators=[alpha_only], # Keep alpha_only or change to alpha_space if you want spaces here too
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        validators=[alpha_space], # CHANGED: Allows "Van Helsing" etc.
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        required=False
    )
    
    remove_image = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ['profile_image', 'first_name', 'last_name', 'bio', 'username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_username'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'id': 'id_email'}), # Added ID
            'profile_image': forms.FileInput(attrs={'class': 'file-input', 'id': 'fileInput'}),
        }

    # --- CLEANING ---
    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')
        if data: return data.title()
        return data

    def clean_last_name(self):
        data = self.cleaned_data.get('last_name')
        if data: return data.title()
        return data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.lower()
            # Check if taken by SOMEONE ELSE (exclude self)
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This username is already taken.")
            return username
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Check if taken by SOMEONE ELSE (exclude self)
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("This email is already registered.")
            return email
        return email
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        # FIX: Add 'or ""' so if it is None, it becomes an empty string.
        # This satisfies the type checker (Sized protocol).
        password = self.cleaned_data.get('new_password1') or ""
        
        # 1. Check Length (8 to 32)
        if len(password) < 8 or len(password) > 32:
            raise forms.ValidationError("Password must be between 8 and 32 characters.")
        
        # 2. Check for at least one Uppercase letter
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # 3. Check for at least one Digit
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
            
        return password