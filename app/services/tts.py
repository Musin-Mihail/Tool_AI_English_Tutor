import hashlib
import os
import shutil
import time
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.paths import TTS_CACHE_DIR, TTS_MODELS_DIR

_KOKORO_FILES = {
    "kokoro-v1.0.onnx": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
        "model-files-v1.0/kokoro-v1.0.onnx"
    ),
    "voices-v1.0.bin": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
        "model-files-v1.0/voices-v1.0.bin"
    ),
}


def pad_audio_slots(paths: List[Optional[str]], size: int = 5) -> List[Optional[str]]:
    out = list(paths[:size])
    while len(out) < size:
        out.append(None)
    return out


def parse_en_variants(en_text_or_list: Any = None, en_text: str = "") -> List[str]:
    """Split English variants from a list or legacy 'a / b' string."""
    from app.data.database import normalize_en_variants

    return normalize_en_variants(en_text_or_list, en_text)


def english_tts_text(en_text: str) -> str:
    """Legacy: first English variant only."""
    variants = parse_en_variants(None, en_text)
    return variants[0] if variants else ""


def _download_file(url: str, dest: Path, retries: int = 5) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    last_error: Exception | None = None
    request = urllib.request.Request(url, headers={"User-Agent": "EnglishTutorAI/1.0"})
    for attempt in range(1, retries + 1):
        try:
            print(
                f"--- Downloading TTS '{dest.name}' (attempt {attempt}/{retries}) ---"
            )
            with urllib.request.urlopen(request, timeout=300) as resp, open(
                tmp, "wb"
            ) as out:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            tmp.replace(dest)
            print(f"--- TTS file ready: {dest} ---")
            return
        except Exception as e:
            last_error = e
            print(f"!!! TTS download failed (attempt {attempt}/{retries}): {e}")
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            if attempt < retries:
                wait_s = min(2**attempt, 30)
                print(f"--- Retrying in {wait_s}s ---")
                time.sleep(wait_s)
    raise RuntimeError(
        f"Failed to download {url} after {retries} attempts."
    ) from last_error


def _ensure_kokoro_files() -> tuple[Path, Path]:
    TTS_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = TTS_MODELS_DIR / "kokoro-v1.0.onnx"
    voices_path = TTS_MODELS_DIR / "voices-v1.0.bin"
    if not model_path.exists():
        _download_file(_KOKORO_FILES["kokoro-v1.0.onnx"], model_path)
    if not voices_path.exists():
        _download_file(_KOKORO_FILES["voices-v1.0.bin"], voices_path)
    return model_path, voices_path


def _lang_for_voice(voice: str) -> str:
    return "en-gb" if (voice or "").lower().startswith("b") else "en-us"


@lru_cache(maxsize=1)
def _get_kokoro():
    from kokoro_onnx import Kokoro

    model_path, voices_path = _ensure_kokoro_files()
    print(f"--- Loading Kokoro TTS from {model_path} ---")
    return Kokoro(str(model_path), str(voices_path))


def preload_tts() -> None:
    if not settings.TTS_ENABLED:
        return
    print("--- Preloading Kokoro TTS ---")
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _get_kokoro()
    print("--- Kokoro TTS ready ---")


def _cache_path(text: str, voice: str) -> Path:
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(f"{voice}|{text}".encode("utf-8")).hexdigest()[:20]
    return TTS_CACHE_DIR / f"{digest}.wav"


def synthesize_text(text: str, voice: Optional[str] = None) -> Optional[str]:
    if not settings.TTS_ENABLED:
        return None
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return None

    voice_name = voice or settings.TTS_VOICE
    dest = _cache_path(cleaned, voice_name)
    if dest.exists():
        return str(dest)

    try:
        import soundfile as sf

        kokoro = _get_kokoro()
        lang = _lang_for_voice(voice_name)
        samples, sample_rate = kokoro.create(
            cleaned,
            voice=voice_name,
            speed=settings.TTS_SPEED,
            lang=lang,
        )
        sf.write(str(dest), samples, sample_rate)
        print(f"[TTS] {cleaned!r} -> {dest.name}")
        return str(dest)
    except Exception as e:
        print(f"!!! TTS failed for {cleaned!r}: {e}")
        if dest.exists():
            try:
                os.remove(dest)
            except OSError:
                pass
        return None


def synthesize_en_variants(
    variants: List[str], voice: Optional[str] = None
) -> List[Optional[str]]:
    """Synthesize each English variant as a separate WAV (max 4)."""
    paths: List[Optional[str]] = []
    for text in (variants or [])[:4]:
        paths.append(synthesize_text(text, voice=voice))
    return pad_audio_slots(paths, size=4)


_play_generation = 0


def remount_audio_paths(paths: List[Optional[str]], size: int = 4) -> List[Optional[str]]:
    """Copy WAVs to unique names so Gradio Audio remounts at position 0."""
    global _play_generation
    _play_generation += 1
    gen = _play_generation
    TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    for old in TTS_CACHE_DIR.glob("ui_play_*.wav"):
        try:
            parts = old.stem.split("_")
            # ui_play_{gen}_{slot}
            if len(parts) >= 4 and int(parts[2]) < gen - 1:
                old.unlink(missing_ok=True)
        except (ValueError, OSError):
            pass

    out: List[Optional[str]] = []
    for i, src in enumerate(pad_audio_slots(list(paths or []), size=size)):
        if not src or not os.path.exists(src):
            out.append(None)
            continue
        dest = TTS_CACHE_DIR / f"ui_play_{gen}_{i}.wav"
        try:
            shutil.copy2(src, dest)
            out.append(str(dest))
        except OSError as e:
            print(f"!!! TTS remount copy failed: {e}")
            out.append(src)
    return out


def synthesize_correct_variants(result: Dict[str, Any]) -> List[Optional[str]]:
    sentences = result.get("sentences_feedback") or []
    paths: List[Optional[str]] = []
    for sentence in sentences[:5]:
        paths.append(synthesize_text(sentence.get("correct_variant") or ""))
    return pad_audio_slots(paths)
