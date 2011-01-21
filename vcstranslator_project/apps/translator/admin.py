from django.contrib import admin

from translator.models import FailedTranslation


admin.site.register(FailedTranslation,
    list_display=["source", "target", "command", "count"],
    ordering=["-count"],
)
