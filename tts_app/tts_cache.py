# tts_cache.py
import asyncio
import edge_tts

_voices_manager = None

async def load_voices_manager():
    global _voices_manager
    if _voices_manager is None:
        _voices_manager = await edge_tts.VoicesManager.create()
    return _voices_manager

def preload_voices_manager():
    # Sync wrapper to run during app startup
    try:
        asyncio.run(load_voices_manager())
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Failed to preload voices: %s", e, exc_info=True)
