from django.urls import path
from .views import *
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .lip_sync import generate_voice_preview


urlpatterns = [
    # path('', index, name='index'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path("", login_required(TemplateView.as_view(template_name="index.html")), name="home"),
    path("text-to-speech/", login_required(TemplateView.as_view(template_name="text_to_speech.html")), name="text_to_speech"),
    path("lip-sync-animation/", lip_sync, name="lip_sync"),
    path("voice-clone/", login_required(TemplateView.as_view(template_name="voice_clone.html")), name="lip_sync"),
    path("api/languages/", get_languages, name="get_languages"),
    path("api/voices/", get_voices, name="get_voices"),
    path("api/tts-preview/", generate_voice_preview, name="tts_preview"),    
    path('api/tts/', text_to_speech, name='text_to_speech'),
    path("api/lip-sync/", lip_sync_api, name="lip_sync_api"),    
    path("api/voice-clone/", voice_clone_view, name="voice_clone"),
]
