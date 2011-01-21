from django.test import TestCase

from translator.forms import TranslationForm
from translator.utils import Translator


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


class TranslatorTests(TestCase):
    def assert_translates(self, translator, command, result):
        r = translator.translate(command)
        self.assertTrue(r.success)
        self.assertEqual(r.result, result)

    def test_svn_to_git(self):
        t = Translator("svn", "git")
        self.assert_translates(t, "commit", "git commit -a")
