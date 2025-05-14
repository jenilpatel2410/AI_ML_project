from django.contrib import admin
from .models import ClonedVoice

# Register your models here.
@admin.register(ClonedVoice)
class ClonedVoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_audio', 'text', 'cloned_audio', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
