from django.test import TestCase

from translator.forms import TranslationForm
from translator.models import FailedTranslation
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

    def assert_cant_handle(self, translator, command):
        r = translator.translate(command)
        self.assertFalse(r.success)
        self.assertTrue(r.result.startswith("We can't handle this yet"))

    def test_svn_to_git(self):
        t = Translator("svn", "git")
        self.assert_translates(t, "commit", "git commit -a")

    def test_cant_handle(self):
        t = Translator("svn", "git")
        self.assert_cant_handle(t, "commit some/file")
        f = FailedTranslation.objects.get()
        self.assertEqual(f.source, "svn")
        self.assertEqual(f.target, "git")
        self.assertEqual(f.command, "commit some/file")
        self.assertEqual(f.count, 1)

        self.assert_cant_handle(t, "commit some/file")
        f = FailedTranslation.objects.get()
        self.assertEqual(f.count, 2)
