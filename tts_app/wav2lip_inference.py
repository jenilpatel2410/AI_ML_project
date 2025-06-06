import os
import subprocess
from django.conf import settings
import cv2
import librosa
from django.conf import settings
import sys

python_executable = sys.executable

WAV2LIP_DIR = os.path.join(settings.BASE_DIR, "Wav2Lip")


def create_video_from_image(image_path, audio_path, output_video, fps=25):
    """Creates a video from an image with a duration matching the audio file."""
    # Get audio duration
    duration = librosa.get_duration(filename=audio_path)

    image = cv2.imread(image_path)
    height, width, layers = image.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Works well for Windows
    video_writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    for _ in range(int(fps * duration)):  # Match video duration to audio duration
        video_writer.write(image)

    video_writer.release()
    
    print('Video created')
    return output_video


def generate_lip_sync_video(image_path, audio_path, output_video, unique_id=None):
    """Generates a lip-sync video using Wav2Lip."""
    base_dir = settings.BASE_DIR
    
    if not unique_id:
        import uuid
        unique_id = str(uuid.uuid4()).split('-')[0]
        
    # Convert image into a video
    temp_video = os.path.join(os.path.dirname(output_video), f"temp_{unique_id}.mp4")
    create_video_from_image(image_path, audio_path, temp_video)

    command = [
        python_executable,
        os.path.join(WAV2LIP_DIR, "inference.py"),
        "--checkpoint_path", os.path.join(WAV2LIP_DIR, "wav2lip_gan.pth"),
        "--face", temp_video,  # Provide video instead of image
        "--audio", audio_path,
        "--outfile", output_video,
        "--resize_factor", '1',
        "--static", 'True',
    ]
    
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if process.returncode == 0:
        if os.path.exists(temp_video):
            os.remove(temp_video)
        return output_video
    else:
        raise Exception(f"Wav2Lip Error: {process.stderr.decode()}")
