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

    def test_x_to_x(self):
        t = Translator("svn", "svn")
        self.assert_translates(t, "log", "svn log")

    def test_svn_to_git(self):
        t = Translator("svn", "git")
        self.assert_translates(t, "commit", "git commit -a && git push")
        self.assert_translates(t, "ci", "git commit -a && git push")
        self.assert_translates(t, "checkout", "git clone")
        self.assert_translates(t, "co", "git clone")
        self.assert_translates(t, "add", "git add")
        self.assert_translates(t, "add file.txt", "git add file.txt")
        self.assert_translates(t, "add some/other/file.txt", "git add some/other/file.txt")
        self.assert_translates(t, "update", "git pull")

    def test_git_to_svn(self):
         t = Translator("git", "svn")
         self.assert_translates(t, "pull", "svn up")
         self.assert_translates(t, "clone", "svn checkout")
         self.assert_translates(t, "status", "svn status")

    def test_hg_to_git(self):
        t = Translator("hg", "git")
        self.assert_translates(t, "pull", "git fetch")
        self.assert_translates(t, "commit", "git commit -a")
        self.assert_translates(t, "push", "git push")
        self.assert_translates(t, "diff", "git diff")

    def test_git_to_hg(self):
        t = Translator("git", "hg")
        self.assert_translates(t, "init", "hg init")
        self.assert_translates(t, "clone", "hg clone")
        self.assert_translates(t, "status", "hg status")
        self.assert_translates(t, "pull", "hg pull -u")
        self.assert_translates(t, "push", "hg push")
        self.assert_translates(t, "diff", "hg diff")

    def test_svn_to_hg(self):
        t = Translator("svn", "hg")
        self.assert_translates(t, "commit", "hg commit && hg push")
        self.assert_translates(t, "checkout", "hg clone")

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

        t = Translator("git", "svn")
        self.assert_cant_handle(t, "commit -a")

        t = Translator("svn", "hg")
        self.assert_cant_handle(t, "commit -a")
