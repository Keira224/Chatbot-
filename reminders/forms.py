from django import forms

from calendar_app.models import AcademicEvent

from .models import ReminderPreference


class ReminderPreferenceForm(forms.ModelForm):
    event_types = forms.MultipleChoiceField(
        label="Types d'evenements a suivre",
        choices=AcademicEvent.EVENT_TYPES,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = ReminderPreference
        fields = ("event_types", "reminder_days", "email_enabled")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["event_types"] = self.instance.selected_event_types()

    def save(self, commit=True):
        preference = super().save(commit=False)
        preference.set_event_types(self.cleaned_data["event_types"])
        if commit:
            preference.save()
        return preference
