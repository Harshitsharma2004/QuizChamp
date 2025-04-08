from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, Interest


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    mobile_no = forms.CharField()
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    profile_image = forms.ImageField(required=False)
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'mobile_no', 'dob', 'gender', 'hobbies', 'qualification', 'profile_image', 'interests']


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "mobile_no", "dob", "gender", "hobbies", "qualification", "interests", "profile_image"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True


class ChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser


class QuestionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")
