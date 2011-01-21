from django import forms

from translator.utils import Translator


class TranslationForm(forms.Form):
    command = forms.CharField(initial="command...")
    vcs = forms.ChoiceField(choices=[("", "Target VCS")] + zip(Translator.targets, Translator.targets))

    def clean_command(self):
        value = self.cleaned_data["command"]
        parts = value.split()
        if parts[0] not in Translator.targets:
            raise forms.ValidationError("Command must start with a valid VCS (%s)." %
                ", ".join(Translator.targets)
            )
        return value
