# import cv2
# import dlib
# import numpy as np
from gtts import gTTS
# import os
# from moviepy import (
#     VideoClip,
#     VideoFileClip,
#     ImageSequenceClip,
#     ImageClip,
#     TextClip,
#     ColorClip,
#     AudioFileClip,
#     AudioClip,
#     CompositeVideoClip
# )
# from django.conf import settings
# import pyttsx3
import asyncio
import random

import edge_tts
from edge_tts import VoicesManager


# # Load dlib's face detector and landmark predictor
# detector = dlib.get_frontal_face_detector()
# predictor = dlib.shape_predictor(os.path.join(settings.BASE_DIR, "shape_predictor_68_face_landmarks.dat"))


async def generate_audio(text, output_audio, gender='female'):
    """Convert text to speech and save as an audio file."""
    # 1. Using gTTS (Google Text-to-Speech)
    # tts = gTTS(text=text, lang="en")
    # tts.save(output_audio)
    # return output_audio

    # 2. Using pyttsx3 (Offline TTS)
    # engine = pyttsx3.init()

    # # Find appropriate voice
    # voices = engine.getProperty('voices')
    # selected_voice = None

    # for voice in voices:
    #     print(f"Voice: {voice.name}, ID: {voice.id}")

    #     if gender == 'male' and ('david' in voice.name.lower() or 'david' in voice.id.lower()):
    #         selected_voice = voice.id
    #         break
    #     elif gender == 'female' and ('zira' in voice.name.lower() or 'zira' in voice.id.lower()):
    #         selected_voice = voice.id
    #         break

    # if selected_voice:
    #     engine.setProperty('voice', selected_voice)
    # else:
    #     print(f"No {gender} voice found. Using default voice.")  # Debugging line
    #     # You can choose to either set a default voice or raise an exception
    #     engine.setProperty('voice', voices[0].id)  # Fallback to the first available voice (default)

    # engine.save_to_file(text, output_audio)
    # engine.runAndWait()
    
    # return output_audio

    # 3. Using edge_tts (Microsoft Edge TTS)
    voices_manager = await edge_tts.VoicesManager.create()
    voices = voices_manager.find(Gender=gender.capitalize(), Language="en")

    if not voices:
        raise ValueError(f"No voices found for gender '{gender}' and language 'en-US'")

    # Select a random voice from the matching voices
    selected_voice = random.choice(voices)["Name"]

    # Create communicator
    communicate = edge_tts.Communicate(text=text, voice=selected_voice)

    # Save the audio output
    await communicate.save(output_audio)

    return output_audio


from deepface import DeepFace

def detect_gender(photo_path):
    objs = DeepFace.analyze(
        img_path = photo_path, actions = ['gender']
    )
    dominant_gender = objs[0]['dominant_gender'].lower()

    # Normalize to "male" or "female"
    if dominant_gender == 'man':
        return 'male'
    elif dominant_gender == 'woman':
        return 'female'
    else:
        return 'unknown'

# def get_mouth_landmarks(image_path):
#     """Detect facial landmarks and return the mouth region points along with the image."""
#     image = cv2.imread(image_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     faces = detector(gray)

#     if len(faces) == 0:
#         print("No face detected.")
#         return None, None

#     shape = predictor(gray, faces[0])
#     mouth_points = np.array([(shape.part(i).x, shape.part(i).y) for i in range(48, 68)])
#     return mouth_points, image


# def animate_lips(image_path, text, output_video):
#     """Generate a realistic lip-sync video by modifying the mouth region."""
#     mouth_landmarks, image = get_mouth_landmarks(image_path)

#     if mouth_landmarks is None:
#         return None

#     audio_path = generate_audio(text, os.path.join(settings.MEDIA_ROOT, "output.mp3"))
#     audio_clip = AudioFileClip(audio_path)

#     # Extract mouth region
#     min_x, min_y = np.min(mouth_landmarks, axis=0)
#     max_x, max_y = np.max(mouth_landmarks, axis=0)
#     mouth_roi = image[min_y:max_y, min_x:max_x]

#     # Generate mouth movement frames
#     frames = []
#     frame_rate = 15  # 15 FPS
#     total_frames = int(audio_clip.duration * frame_rate)  # Ensure enough frames

#     for i in range(total_frames):  # Generate enough frames to match audio
#         scale = 1.0 + 0.1 * np.sin(i / 5.0)  # Dynamic movement pattern
#         modified_image = image.copy()

#         # Resize the mouth region to simulate opening and closing lips
#         new_width = int((max_x - min_x) * scale)
#         new_height = int((max_y - min_y) * scale)
#         resized_mouth = cv2.resize(mouth_roi, (new_width, new_height))

#         # Compute new mouth position
#         center_x, center_y = np.mean(mouth_landmarks, axis=0).astype(int)
#         offset_x = center_x - new_width // 2
#         offset_y = center_y - new_height // 2

#         # Ensure boundaries don't exceed image size
#         offset_x = max(0, min(offset_x, image.shape[1] - new_width))
#         offset_y = max(0, min(offset_y, image.shape[0] - new_height))

#         # Place the resized mouth back into the image
#         modified_image[offset_y:offset_y+new_height, offset_x:offset_x+new_width] = resized_mouth

#         # Convert BGR to RGB for MoviePy
#         frames.append(cv2.cvtColor(modified_image, cv2.COLOR_BGR2RGB))

#     # Create ImageSequenceClip with the correct duration
#     video_clip = ImageSequenceClip(frames, fps=frame_rate).with_duration(audio_clip.duration)

#     # Combine video and audio
#     final_clip = CompositeVideoClip([video_clip]).with_audio(audio_clip)
#     final_clip = final_clip.with_duration(audio_clip.duration)  # Ensure full duration

#     # Save final video
#     final_clip.write_videofile(output_video, codec="libx264", fps=frame_rate)

#     return output_video
