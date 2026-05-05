import io
from PIL import Image
from google.genai import types
from utils.gemini_client import get_client, DEFAULT_IMAGE_MODEL


def _generate_with_imagen(client, prompt, aspect_ratio, num_images, negative_prompt, model):
    config = types.GenerateImagesConfig(
        number_of_images=num_images,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt if negative_prompt else None,
    )
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=config,
    )
    images = []
    for generated_image in response.generated_images:
        img = Image.open(io.BytesIO(generated_image.image.image_bytes))
        images.append(img)
    return images


def _generate_with_gemini(client, prompt, aspect_ratio, num_images, negative_prompt, model):
    # Geminiモデルはgenerate_content + IMAGE modalityで画像生成
    # アスペクト比・枚数はプロンプトに含める形で対応
    aspect_hint = f" Aspect ratio: {aspect_ratio}." if aspect_ratio != "1:1" else ""
    neg_hint = f" Avoid: {negative_prompt}." if negative_prompt else ""
    full_prompt = prompt + aspect_hint + neg_hint

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"],
    )

    images = []
    for _ in range(num_images):
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=config,
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                img = Image.open(io.BytesIO(part.inline_data.data))
                images.append(img)

    return images


def generate_images(
    prompt: str,
    aspect_ratio: str = "1:1",
    num_images: int = 1,
    negative_prompt: str = "",
    model: str = DEFAULT_IMAGE_MODEL,
) -> list[Image.Image]:
    client = get_client()

    if model.startswith("gemini-"):
        return _generate_with_gemini(client, prompt, aspect_ratio, num_images, negative_prompt, model)
    else:
        return _generate_with_imagen(client, prompt, aspect_ratio, num_images, negative_prompt, model)
