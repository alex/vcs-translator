from django.core.management.base import NoArgsCommand

from translator.models import FailedTranslation
from translator.utils import Translator


class Command(NoArgsCommand):
    help = "Checks if there are any failed translations which are now working."

    def handle_noargs(self, *args, **kwargs):
        for f in FailedTranslation.objects.iterator():
            t = Translator(f.source, f.target)
            res = t.translate(f.command)
            if res.success:
                print "#%d: %s %s -> %s Successfully translated: %s" % (
                    f.pk, f.source, f.command, f.target, res.result
                )
