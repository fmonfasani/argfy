# backend/app/utils/emoji_log.py
from app.config import settings 
def e(text: str) -> str:
    """Devuelve el texto con emoji solo si LOG_EMOJIS está activo."""
    return text if settings.LOG_EMOJIS else text.encode('ascii', 'ignore').decode()
