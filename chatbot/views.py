from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import ChatQuestionForm
from .models import ChatMessage
from .services import answer_question


@login_required
def chat(request):
    if request.method == "POST":
        form = ChatQuestionForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data["question"]
            answer = answer_question(question)
            ChatMessage.objects.create(user=request.user, question=question, answer=answer)
    else:
        form = ChatQuestionForm()

    recent_messages = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:12]
    messages = list(reversed(recent_messages))
    last_message = messages[-1] if messages else None
    suggestions = [
        "Quelles sont les prochaines dates importantes ?",
        "Quand commencent les examens ?",
        "Quelle est la date limite d'inscription ?",
        "Quand aura lieu la prochaine reunion ?",
        "Quels evenements arrivent cette semaine ?",
    ]
    return render(
        request,
        "chatbot/chat.html",
        {
            "form": form,
            "messages": messages,
            "last_message": last_message,
            "suggestions": suggestions,
        },
    )
