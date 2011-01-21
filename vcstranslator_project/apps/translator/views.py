from django.shortcuts import render_to_response
from django.template import RequestContext

from translator.forms import TranslationForm


def home(request):
    form = TranslationForm(request.GET or None)
    results = None
    if form.is_valid():
        results = form.translate()
    return render_to_response("translator/home.html", {
        "form": form,
        "results": results,
    }, context_instance=RequestContext(request))
