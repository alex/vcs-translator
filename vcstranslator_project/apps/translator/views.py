from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from translator.forms import TranslationForm, TranslationFeedbackForm


def home(request):
    form = TranslationForm(request.GET or None)
    results = None
    if form.is_valid():
        results = form.translate()
        request.session["last_translation"] = form.get_data()
    return render_to_response("translator/home.html", {
        "form": form,
        "results": results,
    }, context_instance=RequestContext(request))

def feedback(request):
    if request.method == "POST":
        form = TranslationFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "We got your feedback, thanks!")
            return redirect("home")
    else:
        form = TranslationFeedbackForm(
            initial=request.session.pop("last_translation", None)
        )
    return render_to_response("translator/feedback.html", {
        "form": form,
    }, context_instance=RequestContext(request))
