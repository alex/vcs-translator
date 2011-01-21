from django import forms

from translator.models import TranslationFeedback
from translator.utils import Translator


class TranslationForm(forms.Form):
    command = forms.CharField(initial="command...")
    vcs = forms.ChoiceField(choices=[("", "Target VCS")] + zip(Translator.vcs, Translator.vcs))

    def clean_command(self):
        value = self.cleaned_data["command"]
        parts = value.split()
        if parts[0] not in Translator.vcs:
            raise forms.ValidationError("Command must start with a valid VCS (%s)." %
                ", ".join(Translator.vcs)
            )
        return value

    def get_data(self):
        assert self.is_valid()
        return {
            "source": self.cleaned_data["command"].split()[0],
            "target": self.cleaned_data["vcs"],
            "command": self.cleaned_data["command"],
        }

    def translate(self):
        assert self.is_valid()
        data = self.cleaned_data
        command, rest = data["command"].split(" ", 1)
        return Translator(command.split()[0], data["vcs"]).translate(rest)


class TranslationFeedbackForm(forms.ModelForm):
    command = forms.CharField()

    class Meta:
        model = TranslationFeedback
