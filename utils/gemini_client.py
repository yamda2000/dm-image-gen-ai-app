import contextvars
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

DEFAULT_TEXT_MODEL = "gemini-2.0-flash"
DEFAULT_IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"

AVAILABLE_IMAGE_MODELS = {
    "Gemini 2.0 Flash Image (プレビュー)": "gemini-2.0-flash-preview-image-generation",
}

_session_api_key: contextvars.ContextVar[str] = contextvars.ContextVar("session_api_key", default="")


def set_session_api_key(key: str) -> None:
    _session_api_key.set(key)


def get_client() -> genai.Client:
    api_key = _session_api_key.get() or os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("GEMINI_API_KEY が設定されていません。.env ファイルまたはサイドバーでAPIキーを入力してください。")
    return genai.Client(api_key=api_key)


def generate_text(prompt: str, model_name: str = DEFAULT_TEXT_MODEL) -> str:
    client = get_client()
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text
