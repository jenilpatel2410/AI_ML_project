import cv2
import dlib
import numpy as np
from gtts import gTTS
import os
from moviepy import (
    VideoClip,
    VideoFileClip,
    ImageSequenceClip,
    ImageClip,
    TextClip,
    ColorClip,
    AudioFileClip,
    AudioClip,
    CompositeVideoClip
)
from django.conf import settings
# import phonemizer


# Load dlib's face detector and landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(os.path.join(settings.BASE_DIR, "shape_predictor_68_face_landmarks.dat"))

# from phonemizer.backend.espeak.wrapper import EspeakWrapper
# _ESPEAK_LIBRARY = 'C:\Program Files\eSpeak NG\libespeak-ng.dll'
# EspeakWrapper.set_library(_ESPEAK_LIBRARY)

# PHONEME_MOUTH_MAP = {
#     "A": (1.5, 1.2),  # Wide open (as in "apple")
#     "E": (1.3, 1.1),  # Slightly open, stretched sideways (as in "eat")
#     "I": (1.1, 1.0),  # Neutral (as in "bit")
#     "O": (1.4, 1.3),  # Circular open (as in "orange")
#     "U": (1.3, 1.4),  # Rounded lips (as in "blue")
#     "M": (0.9, 0.9),  # Closed lips (as in "mmm")
#     "B": (0.9, 0.9),  # Similar to "M" (as in "boy")
#     "P": (0.9, 0.9),  # Similar to "M" and "B" (as in "pop")
#     "S": (1.0, 1.0),  # Neutral (as in "snake")
#     "T": (1.0, 1.0),  # Neutral (as in "top")
#     "F": (1.0, 0.8),  # Upper teeth touching lower lip (as in "fire")
#     "V": (1.0, 0.8),  # Same as "F" but softer (as in "very")
#     "L": (1.1, 1.0),  # Tongue touches top teeth (as in "love")
#     "W": (1.3, 1.4),  # Rounded lips, close together (as in "wow")
#     "R": (1.1, 1.2),  # Slightly open, lips forward (as in "red")
#     "CH": (1.2, 1.0),  # Lips pushed slightly forward (as in "cheese")
#     "SH": (1.2, 1.0),  # Similar to "CH" (as in "she")
#     "TH": (1.1, 1.0),  # Tongue between teeth (as in "this")
#     "Z": (1.0, 1.0),  # Neutral (as in "zebra")
# }


def generate_audio(text, output_audio):
    """Convert text to speech and save as an audio file."""
    tts = gTTS(text=text, lang="en")
    tts.save(output_audio)
    return output_audio

def get_mouth_landmarks(image_path):
    """Detect facial landmarks and return the mouth region points along with the image."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if len(faces) == 0:
        print("No face detected.")
        return None, None

    shape = predictor(gray, faces[0])
    mouth_points = np.array([(shape.part(i).x, shape.part(i).y) for i in range(48, 68)])
    return mouth_points, image

# def text_to_phonemes(text):
#     """Convert text to phonemes using phonemizer library."""
#     phonemes = phonemizer.phonemize(text, language="en-us", backend="espeak")
#     return list(phonemes.replace(" ", "").upper())  # Remove spaces and convert to uppercase

# def apply_affine_transform(src_img, src_pts, dst_pts, size):
#     """Warp the mouth region based on phoneme shape changes."""
#     warp_mat = cv2.getAffineTransform(np.float32(src_pts), np.float32(dst_pts))
#     return cv2.warpAffine(src_img, warp_mat, size, borderMode=cv2.BORDER_REFLECT_101)

# def animate_lips(image_path, text, output_video):
#     """Generate a realistic lip-sync video by modifying the mouth region based on phonemes."""
#     mouth_landmarks, image = get_mouth_landmarks(image_path)
#     if mouth_landmarks is None:
#         return None

#     audio_path = generate_audio(text, os.path.join(settings.MEDIA_ROOT, "output.mp3"))
#     audio_clip = AudioFileClip(audio_path)

#     phonemes = text_to_phonemes(text)
#     total_frames = int(audio_clip.duration * 15)  # 15 FPS

#     x, y, w, h = cv2.boundingRect(mouth_landmarks)

#     frames = []
#     for i in range(total_frames):
#         phoneme = phonemes[i % len(phonemes)]  # Loop through phonemes
#         scale_x, scale_y = PHONEME_MOUTH_MAP.get(phoneme, (1.0, 1.0))

#         modified_image = image.copy()
#         mouth_region = modified_image[y:y+h, x:x+w].copy()

#         # Scale and shift lips to simulate real movement
#         mouth_center = np.mean(mouth_landmarks, axis=0).astype(int)
#         scaled_mouth = (mouth_landmarks - mouth_center) * [scale_x, scale_y] + mouth_center

#         # Apply affine transformation to warp the mouth shape
#         for j in range(len(mouth_landmarks) - 2):
#             src_triangle = [mouth_landmarks[j], mouth_landmarks[j+1], mouth_landmarks[j+2]]
#             dst_triangle = [scaled_mouth[j], scaled_mouth[j+1], scaled_mouth[j+2]]

#             warped_mouth = apply_affine_transform(mouth_region, src_triangle, dst_triangle, (w, h))

#             # Blend warped mouth into face
#             modified_image[y:y+h, x:x+w] = cv2.seamlessClone(
#                 warped_mouth, modified_image[y:y+h, x:x+w], np.full((h, w, 3), 255, dtype=np.uint8), (w//2, h//2), cv2.NORMAL_CLONE
#             )

#         frames.append(cv2.cvtColor(modified_image, cv2.COLOR_BGR2RGB))

#     video_clip = ImageSequenceClip(frames, fps=15).with_duration(audio_clip.duration)
#     final_clip = CompositeVideoClip([video_clip]).with_audio(audio_clip)
#     final_clip = final_clip.with_duration(audio_clip.duration)
#     final_clip.write_videofile(output_video, codec="libx264", fps=15)

#     return output_video


def animate_lips(image_path, text, output_video):
    """Generate a realistic lip-sync video by modifying the mouth region."""
    mouth_landmarks, image = get_mouth_landmarks(image_path)

    if mouth_landmarks is None:
        return None

    audio_path = generate_audio(text, os.path.join(settings.MEDIA_ROOT, "output.mp3"))
    audio_clip = AudioFileClip(audio_path)

    # Extract mouth region
    min_x, min_y = np.min(mouth_landmarks, axis=0)
    max_x, max_y = np.max(mouth_landmarks, axis=0)
    mouth_roi = image[min_y:max_y, min_x:max_x]

    # Generate mouth movement frames
    frames = []
    frame_rate = 15  # 15 FPS
    total_frames = int(audio_clip.duration * frame_rate)  # Ensure enough frames

    for i in range(total_frames):  # Generate enough frames to match audio
        scale = 1.0 + 0.1 * np.sin(i / 5.0)  # Dynamic movement pattern
        modified_image = image.copy()

        # Resize the mouth region to simulate opening and closing lips
        new_width = int((max_x - min_x) * scale)
        new_height = int((max_y - min_y) * scale)
        resized_mouth = cv2.resize(mouth_roi, (new_width, new_height))

        # Compute new mouth position
        center_x, center_y = np.mean(mouth_landmarks, axis=0).astype(int)
        offset_x = center_x - new_width // 2
        offset_y = center_y - new_height // 2

        # Ensure boundaries don't exceed image size
        offset_x = max(0, min(offset_x, image.shape[1] - new_width))
        offset_y = max(0, min(offset_y, image.shape[0] - new_height))

        # Place the resized mouth back into the image
        modified_image[offset_y:offset_y+new_height, offset_x:offset_x+new_width] = resized_mouth

        # Convert BGR to RGB for MoviePy
        frames.append(cv2.cvtColor(modified_image, cv2.COLOR_BGR2RGB))

    # Create ImageSequenceClip with the correct duration
    video_clip = ImageSequenceClip(frames, fps=frame_rate).with_duration(audio_clip.duration)

    # Combine video and audio
    final_clip = CompositeVideoClip([video_clip]).with_audio(audio_clip)
    final_clip = final_clip.with_duration(audio_clip.duration)  # Ensure full duration

    # Save final video
    final_clip.write_videofile(output_video, codec="libx264", fps=frame_rate)

    return output_video
