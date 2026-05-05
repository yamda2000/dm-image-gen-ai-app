from google.genai import types
from utils.gemini_client import get_client, DEFAULT_TEXT_MODEL


def create_edit_prompt(image_bytes: bytes, edit_instruction: str) -> str:
    """画像と編集指示からより良いプロンプトを生成する"""
    client = get_client()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    meta_prompt = f"""
この画像を分析し、以下の編集指示を反映した新しいAI画像生成プロンプトを作成してください。

編集指示: {edit_instruction}

元の画像の特徴（スタイル、構図、色調など）を保ちつつ、指示された変更を加えた
新しい画像を生成するための英語プロンプトを作成してください。
プロンプトの後に日本語での説明も添えてください。

形式:
**生成プロンプト（英語）**
（プロンプト）

**内容説明（日本語）**
（説明）
"""

    response = client.models.generate_content(
        model=DEFAULT_TEXT_MODEL,
        contents=[image_part, meta_prompt],
    )

    return response.text
