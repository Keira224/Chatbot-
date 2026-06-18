from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import StudentProfile


class StudentRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        label="Type de compte",
        choices=StudentProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
    )
    first_name = forms.CharField(label="Prenom", max_length=150)
    last_name = forms.CharField(label="Nom", max_length=150)
    email = forms.EmailField(label="Email")
    student_number = forms.CharField(label="Matricule ou identifiant", max_length=30, required=False)
    program = forms.CharField(label="Filiere ou departement", max_length=120, required=False)
    level = forms.CharField(label="Niveau ou fonction", max_length=80, required=False)
    phone = forms.CharField(label="Telephone", max_length=30, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte utilise deja cette adresse email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                role=self.cleaned_data["role"],
                student_number=self.cleaned_data.get("student_number", ""),
                program=self.cleaned_data.get("program", ""),
                level=self.cleaned_data.get("level", ""),
                phone=self.cleaned_data.get("phone", ""),
            )
        return user
