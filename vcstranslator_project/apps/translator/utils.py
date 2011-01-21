from django.utils.datastructures import SortedDict


class BaseTranslator(object):
    def translate(self, command):
        meth = getattr(self, "translate_%s" % command.__class__.__name__.lower())
        try:
            result = meth(command)
        except CandHandleYet:
            return TranslationFailure("Can't yet handle this")
        except CantHandle:
            return TranslationFailure("This VCS doesn't support this operation")
        else:
            return TranslationSuccess(result)

class GitTranslator(BaseTranslator):
    def translate_commit(self, command):
        if command.files is command.ALL:
            return "git commit -a"

class HgTranslator(BaseTranslator):
    pass

class SVNTranslator(BaseTranslator):
    def parse(self, command):
        part, = command.split()
        if part == "commit":
            return Commit(files=Commit.ALL)

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

    def translate(self, command):
        parsed = self.vcs[self.source]().parse(command)
        return self.vcs[self.target]().translate(parsed)


class TranslationResult(object):
    def __init__(self, result):
        self.result = result

class TranslationFailure(TranslationResult):
    success = False

class TranslationSuccess(TranslationResult):
    success = True

class Command(object):
    ALL = object()

class Commit(Command):
    def __init__(self, files):
        self.files = files
