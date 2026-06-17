from django import forms

from .models import AcademicEvent


class EventSearchForm(forms.Form):
    q = forms.CharField(label="Recherche", required=False)
    event_type = forms.ChoiceField(
        label="Type",
        required=False,
        choices=[("", "Tous les types")] + AcademicEvent.EVENT_TYPES,
    )


class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = ("title", "description", "event_type", "start_date", "end_date", "location")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and end_date < start_date:
            self.add_error("end_date", "La date de fin doit etre superieure ou egale a la date de debut.")
        return cleaned_data
