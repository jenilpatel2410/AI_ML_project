from django.apps import AppConfig
from .tts_cache import preload_voices_manager

class TtsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tts_app'

    def ready(self):
        from TTS.api import TTS
        import torch
        from TTS.tts.configs.xtts_config import XttsConfig, XttsAudioConfig, XttsArgs
        from TTS.config.shared_configs import BaseDatasetConfig

        torch.serialization.add_safe_globals([
            XttsConfig,
            XttsAudioConfig,
            BaseDatasetConfig,
            XttsArgs,
        ])

        device = "cuda" if torch.cuda.is_available() else "cpu"

        from . import tts_singleton
        tts_singleton.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)

        preload_voices_manager()