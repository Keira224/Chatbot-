from django import forms


class ChatQuestionForm(forms.Form):
    question = forms.CharField(
        label="Votre question",
        widget=forms.TextInput(attrs={"placeholder": "Ex: Quand commencent les examens ?"}),
    )
