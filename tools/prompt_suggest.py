from utils.gemini_client import generate_text


def suggest_prompts(theme: str, style: str, count: int = 5) -> str:
    prompt = f"""
あなたはAI画像生成の専門家です。
以下のテーマとスタイルに合った、高品質な画像を生成するためのプロンプトを{count}個作成してください。

テーマ: {theme}
スタイル: {style}

条件:
- 各プロンプトは英語で記述してください
- 各プロンプトは具体的で詳細な描写を含めてください
- 照明、構図、雰囲気、色調なども含めてください
- Imagen 3やMidjourney等のAI画像生成ツールで使えるクオリティにしてください
- 日本語での補足説明も各プロンプトの後に添えてください

形式:
**プロンプト1**
（英語プロンプト）
→（日本語での内容説明）

のように番号付きで出力してください。
"""
    return generate_text(prompt)
