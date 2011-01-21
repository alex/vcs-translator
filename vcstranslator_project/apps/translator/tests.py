from django.test import TestCase

from translator.forms import TranslationForm


class TranslationFormTests(TestCase):
    def test_clean_command(self):
        f = TranslationForm({"command": ""})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors["command"], ["This field is required."])

        f = TranslationForm({"command": "bzr commit", "vcs": "git"})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors["command"], ["Command must start with a valid VCS (git, hg, svn)."])

        f = TranslationForm({"command": "svn commit", "vcs": "git"})
        self.assertTrue(f.is_valid())
