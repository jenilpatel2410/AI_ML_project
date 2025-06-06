import os
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth.forms import AuthenticationForm
from gtts import gTTS
from rest_framework.decorators import api_view
from django.conf import settings
from django.core.files.storage import default_storage
from .lip_sync import generate_audio, detect_gender
from .wav2lip_inference import generate_lip_sync_video
from django.contrib.auth.decorators import login_required
from .forms import EmailAuthenticationForm
from .models import ClonedVoice
from TTS.api import TTS
import uuid, torch, asyncio
from .tts_singleton import tts
import edge_tts
import logging
from .tts_cache import load_voices_manager

logger = logging.getLogger(__name__)

@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def lip_sync(request):
    voices = ClonedVoice.objects.filter(user=request.user)
    return render(request, 'lip_sync.html', {'cloned_voices': voices})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@api_view(['POST'])
def text_to_speech(request):
    try:
        text = request.data.get('text', '')
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        gender = request.data.get('gender', 'female')
        voice_select = request.data.get('voice_id', None)
        
        output_dir = os.path.join(settings.MEDIA_ROOT, 'texttospeech')
        os.makedirs(output_dir, exist_ok=True)
        
        # tts = gTTS(text=text, lang='en')  # Convert text to speech
        unique_id = str(uuid.uuid4()).split('-')[0]
        filename = f'tts_{unique_id}.mp3'
        file_path = os.path.join(output_dir, filename)
        # tts.save(file_path)  # Save the speech file

        asyncio.run(generate_audio(text, file_path, gender=gender, voice_id=voice_select))

        audio_url = settings.MEDIA_URL + f'texttospeech/{filename}'
        return JsonResponse({'audio_url': audio_url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from babel import Locale

def get_language_name(locale_code):
    try:
        lang, country = locale_code.split("-")
        return Locale(lang, country).get_display_name("en").title()
    except Exception:
        return locale_code  # fallback


async def get_languages(request):
    try:
        voices_manager = await load_voices_manager()
        voices = voices_manager.voices
        languages = sorted(set(v["Locale"] for v in voices))
        language_data = [
            {"code": lang, "name": get_language_name(lang)}
            for lang in languages
        ]
        return JsonResponse(language_data, safe=False)
    except Exception as e:
        logger.error("Error in get_languages: %s", e, exc_info=True)
        return JsonResponse({"error": "Internal Server Error"}, status=500)


async def get_voices(request):
    language = request.GET.get("language", "en-US")
    gender = request.GET.get('gender', 'female')

    if not language or not gender:
        return JsonResponse({"error": "Missing language or gender"}, status=400)

    try:
        voices_manager = await load_voices_manager()
        voices = voices_manager.find(Locale=language, Gender=gender.capitalize())

        return JsonResponse([
            {"name": v["FriendlyName"], "short_name": v["ShortName"]}
            for v in voices
        ], safe=False)
    except Exception as e:
        logger.error("Error in get_voices: %s", e, exc_info=True)
        return JsonResponse({"error": "Internal Server Error"}, status=500)




@api_view(['POST'])
def lip_sync_api(request):
    image = request.FILES.get("image")
    text = request.POST.get("text")
    voice_id = request.POST.get("voice_id")

    if not image or not text:
        return JsonResponse({"error": "Image and text are required"}, status=400)

    if voice_id:
        try:
            voice_record = ClonedVoice.objects.get(id=voice_id, user=request.user)
        except ClonedVoice.DoesNotExist:
            return JsonResponse({"error": "Invalid voice selected."}, status=400)
    else:
        # fallback or reject if required
        return JsonResponse({"error": "No voice selected."}, status=400)
    
    uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # Generate a shorter unique filename for the image using the first 8 characters of the UUID
    image_unique_id = str(uuid.uuid4()).split('-')[0]
    image_filename = f"image_{image_unique_id}{os.path.splitext(image.name)[-1]}"
    image_path = os.path.join(uploads_dir, image_filename)

    # Save the uploaded image
    with default_storage.open(image_path, "wb+") as destination:
        for chunk in image.chunks():
            destination.write(chunk)

    # # Generate lip-sync video
    # output_video = os.path.join(settings.MEDIA_ROOT, "videos", "lip_sync.mp4")
    # result = animate_lips(image_path, text, output_video)

    # if result:
    #     return JsonResponse({"video_url": settings.MEDIA_URL + "videos/lip_sync.mp4"})
    # else:
    #     return JsonResponse({"error": "Could not process the image."}, status=500)


    # gender = "male" #detect_gender(image_path)
    # print(f"Detected Gender: {gender}")
    audio_filename = f"speech_{image_unique_id}.wav"
    audio_path = os.path.join(settings.MEDIA_ROOT, "speech", audio_filename)
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    # asyncio.run(generate_audio(text, audio_path, gender=gender))

    tts.tts_to_file(text=text, speaker_wav=voice_record.original_audio, language=voice_record.language, file_path=audio_path)
    print('Audio generated')
    logger.info(f"Audio generated at {audio_path}")
    # Generate lip-sync video using Wav2Lip
    output_video_filename = f"output_video_{image_unique_id}.mp4"
    output_video_path = os.path.join(settings.MEDIA_ROOT, "videos", output_video_filename)
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

    result = generate_lip_sync_video(image_path, audio_path, output_video_path, unique_id=image_unique_id)

    if result:
        video_url = settings.MEDIA_URL + f"videos/{output_video_filename}"
        return JsonResponse({"video_url": video_url})
    else:
        return JsonResponse({"error": "Could not process the image."}, status=500)
    
    
@api_view(['POST'])
def voice_clone_view(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        text = request.POST.get('text')
        language = request.POST.get('language', 'en')

        unique_id = str(uuid.uuid4()).split('-')[0]
        input_filename = f"{unique_id}_{audio_file.name}"
        input_path = os.path.join(settings.MEDIA_ROOT, 'cloned_voices', 'originals', input_filename)

        # Save uploaded reference audio
        os.makedirs(os.path.dirname(input_path), exist_ok=True)
        with open(input_path, 'wb+') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # Generate cloned output
        output_filename = f"{unique_id}_cloned.wav"
        output_path = os.path.join(settings.MEDIA_ROOT, 'cloned_voices', 'outputs', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Run TTS
        tts.tts_to_file(text=text, speaker_wav=input_path, language=language, file_path=output_path)

        # Save record in DB
        cloned_voice = ClonedVoice.objects.create(
            user=request.user,
            original_audio=f'cloned_voices/originals/{input_filename}',
            cloned_audio=f'cloned_voices/outputs/{output_filename}',
            text=text,
            language=language
        )

        return JsonResponse({
            'audio_url': cloned_voice.cloned_audio.url
        })

    return render(request, 'voice_clone.html')
    