from django.db.models import F
from django.utils.datastructures import SortedDict

from translator.models import FailedTranslation


class BaseTranslator(object):
    def parse(self, command):
        pass

    def translate(self, command):
        try:
            meth = getattr(self, "translate_%s" % command.__class__.__name__.lower())
        except AttributeError:
            raise CantHandleYet
        return meth(command)

class GitTranslator(BaseTranslator):
    def parse(self, command):
        parts = command.split()
        if parts == ["init"]:
            return Init()
        elif parts == ["pull"]:
            return Pull()
        elif parts == ["clone"]:
            return Clone()
        elif parts == ["status"]:
            return Status()

    def translate_commit(self, command):
        if command.files is command.ALL:
            s = "git commit -a"
        else:
            return
        if command.push:
            s += " && git push"
        return s

    def translate_fetch(self, command):
        return "git fetch"

    def translate_clone(self, command):
        return "git clone"

    def translate_add(self, command):
        cmd = "git add"
        if command.files:
            cmd += " %s" % " ".join(f.path for f in command.files)
        return cmd

    def translate_pull(self, command):
        return "git pull"

class HgTranslator(BaseTranslator):
    def parse(self, command):
        parts = command.split()
        if parts == ["pull"]:
            return Fetch()
        elif parts == ["commit"]:
            return Commit(files=Commit.ALL, push=False)

    def translate_commit(self, command):
        if command.files is command.ALL:
            s = "hg commit"
        else:
            return
        if command.push:
            s += " && hg push"
        return s

    def translate_init(self, command):
        return "hg init"

    def translate_clone(self, command):
        return "hg clone"

    def translate_status(self, command):
        return "hg status"

    def translate_pull(self, command):
        return "hg pull -u"

class SVNTranslator(BaseTranslator):
    def parse(self, command):
        parts = command.split()
        if parts == ["commit"]:
            return Commit(files=Commit.ALL, push=True)
        elif parts in [["checkout"], ["co"]]:
            return Clone()
        elif parts in [["up"], ["update"]]:
            return Pull()
        elif parts[0] in "add" and len(parts) <= 2:
            files = [SomeFile(f) for f in parts[1:]]
            return Add(files=files)

    def translate_pull(self, command):
        return "svn up"

    def translate_clone(self, command):
        return "svn checkout"

class Translator(object):
    vcs = SortedDict([
        ("git", GitTranslator),
        ("hg", HgTranslator),
        ("svn", SVNTranslator),
    ])


    def __init__(self, source, target):
        assert source in self.vcs and target in self.vcs
        self.source = source
        self.target = target

    def handle_step(self, command, step, *args, **kwargs):
        try:
            res = step(*args, **kwargs)
            if res is None:
                raise CantHandleYet
        except CantHandleYet:
            f, _ = FailedTranslation.objects.get_or_create(
                source=self.source,
                target=self.target,
                command=command,
            )
            FailedTranslation.objects.filter(pk=f.pk).update(count=F("count") + 1)
            return TranslationFailure("We can't handle this yet, we've let the monkeys^W programmers in the back room know."), False
        except CantHandle:
            return TranslationFailure("This VCS doesn't support this operation"), False
        return res, True


    def translate(self, command):
        if self.source == self.target:
            return TranslationSuccess("%s %s" % (self.target, command))
        parsed, cont = self.handle_step(command, self.vcs[self.source]().parse, command)
        if not cont:
            return parsed
        res, cont = self.handle_step(command, self.vcs[self.target]().translate, parsed)
        if cont:
            res = TranslationSuccess(res)
        return res


class CantHandleYet(Exception):
    pass

class CantHandle(Exception):
    pass


class TranslationResult(object):
    def __init__(self, result):
        self.result = result

class TranslationFailure(TranslationResult):
    success = False

class TranslationSuccess(TranslationResult):
    success = True


class SomeFile(object):
    def __init__(self, path):
        self.path = path

class Command(object):
    ALL = object()

class Init(Command):
    pass

class Commit(Command):
    def __init__(self, files, push):
        self.files = files
        self.push = push

class Fetch(Command):
    pass

class Pull(Command):
    pass

class Clone(Command):
    pass

class Add(Command):
    def __init__(self, files):
        self.files = files

class Status(Command):
    pass
