from django.urls import path
from .views import text_to_speech, index, lip_sync_api
from django.views.generic import TemplateView


urlpatterns = [
    # path('', index, name='index'),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("text-to-speech/", TemplateView.as_view(template_name="text_to_speech.html"), name="text_to_speech"),
    path("lip-sync-animation/", TemplateView.as_view(template_name="lip_sync.html"), name="lip_sync"),    
    path('api/tts/', text_to_speech, name='text_to_speech'),
    path("api/lip-sync/", lip_sync_api, name="lip_sync_api"),    
]
