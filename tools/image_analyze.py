from google.genai import types
from utils.gemini_client import get_client, DEFAULT_TEXT_MODEL


ANALYSIS_PROMPTS = {
    "詳細説明": "この画像を詳しく説明してください。構図、色彩、被写体、雰囲気など、見えるすべての要素を日本語で説明してください。",
    "シーン解析": "この画像のシーンや状況を分析してください。何が起きているのか、どんな場所か、時間帯や季節なども含めて日本語で説明してください。",
    "画風・スタイル分析": "この画像のアート・写真スタイルを分析してください。画風、技法、雰囲気、参考にしたと思われるスタイルなどを日本語で説明してください。",
    "プロンプト逆生成": "この画像を生成するためのAI画像生成プロンプトを英語で作成してください。Stable DiffusionやMidjourneyで使えるような詳細なプロンプトにしてください。",
    "改善提案": "この画像の改善点や、より良くするためのアドバイスを日本語で提案してください。",
}


def analyze_image(image_bytes: bytes, analysis_type: str = "詳細説明") -> str:
    client = get_client()

    prompt = ANALYSIS_PROMPTS.get(analysis_type, ANALYSIS_PROMPTS["詳細説明"])

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    response = client.models.generate_content(
        model=DEFAULT_TEXT_MODEL,
        contents=[image_part, prompt],
    )

    return response.text
