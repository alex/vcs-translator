from django.contrib import admin

from translator.models import FailedTranslation, TranslationFeedback


admin.site.register(FailedTranslation,
    list_display=["pk", "source", "command", "target", "count"],
    ordering=["-count"],
)
admin.site.register(TranslationFeedback,
    list_display=["pk", "source", "command", "target", "comments"],
)
