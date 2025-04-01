import os
from django.http import JsonResponse
from django.shortcuts import render
from gtts import gTTS
from rest_framework.decorators import api_view
from django.conf import settings
from django.core.files.storage import default_storage
from .lip_sync import animate_lips, generate_audio
from .wav2lip_inference import generate_lip_sync_video


def index(request):
    return render(request, 'index.html')

def lip_sync(request):
    return render(request, 'lip_sync.html')


@api_view(['POST'])
def text_to_speech(request):
    try:
        text = request.data.get('text', '')
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        tts = gTTS(text=text, lang='en')  # Convert text to speech
        file_path = os.path.join(settings.MEDIA_ROOT, 'tts_speech.mp3')
        tts.save(file_path)  # Save the speech file

        return JsonResponse({'audio_url': settings.MEDIA_URL + 'tts_speech.mp3'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@api_view(['POST'])
def lip_sync_api(request):
    image = request.FILES.get("image")
    text = request.POST.get("text")

    if not image or not text:
        return JsonResponse({"error": "Image and text are required"}, status=400)

    # Save the uploaded image
    image_path = os.path.join(settings.MEDIA_ROOT, "uploads", image.name)
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


    audio_path = os.path.join(settings.MEDIA_ROOT, "speech.wav")
    generate_audio(text, audio_path)

    print('Audio generated')
    # Generate lip-sync video using Wav2Lip
    output_video = os.path.join(settings.MEDIA_ROOT, "output_video.mp4")
    # try:
    result = generate_lip_sync_video(image_path, audio_path, output_video)
    return JsonResponse({"video_url": settings.MEDIA_URL + "output_video.mp4"})
    # except Exception as e:
    #     return JsonResponse({"error": str(e)}, status=500)
    