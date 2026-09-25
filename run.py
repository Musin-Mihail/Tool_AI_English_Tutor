import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# Hugging Face: длинный таймаут для больших моделей (large-v3 ~3 ГБ)
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")

if __name__ == "__main__":
    from app.core.config import settings
    from app.services.asr import configure_cuda_runtime_path

    if settings.HF_TOKEN:
        os.environ["HF_TOKEN"] = settings.HF_TOKEN
        os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.HF_TOKEN
        print("--- Hugging Face token configured ---")

    # PATH к cublas64_12.dll нужно выставить до первого CUDA-инференса
    configure_cuda_runtime_path()

    if settings.ASR_PRELOAD:
        from app.services.asr import preload_whisper_model

        try:
            preload_whisper_model()
        except Exception as e:
            print(f"!!! FATAL: Whisper preload failed: {e}")
            print(
                "Сервер не запущен. Проверьте доступ к huggingface.co "
                "и CUDA-библиотеки (nvidia-cublas-cu12), затем перезапустите."
            )
            sys.exit(1)

        if settings.ACOUSTIC_ASR:
            from app.services.acoustic_asr import preload_acoustic_asr

            try:
                preload_acoustic_asr()
            except Exception as e:
                print(f"!!! Acoustic ASR preload failed: {e}")
                print("Продолжаем без wav2vec2 — будет только Whisper.")

    if settings.TTS_ENABLED and settings.TTS_PRELOAD:
        from app.services.tts import preload_tts

        try:
            preload_tts()
        except Exception as e:
            print(f"!!! TTS preload failed: {e}")
            print("Сервер запущен, но озвучка правильного варианта недоступна.")

    from app.ui import FLASHCARD_CSS, build_ui

    demo = build_ui()
    print("--- Open http://127.0.0.1:8000 in your browser ---")
    demo.launch(server_name="127.0.0.1", server_port=8000, css=FLASHCARD_CSS)
