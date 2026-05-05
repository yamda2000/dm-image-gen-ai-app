import io
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.gemini_client import set_session_api_key, AVAILABLE_IMAGE_MODELS

try:
    if "GEMINI_API_KEY" in st.secrets:
        set_session_api_key(st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

from tools.image_gen import generate_images
from tools.image_analyze import analyze_image, ANALYSIS_PROMPTS
from tools.prompt_suggest import suggest_prompts
from tools.image_edit_prompt import create_edit_prompt

st.set_page_config(
    page_title="AI 画像生成ツール",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: bold; color: #7c3aed; margin-bottom: 0.2rem; }
    .sub-title { font-size: 0.95rem; color: #666; margin-bottom: 1.5rem; }
    .result-box {
        background: #f8f9fa;
        border-left: 4px solid #7c3aed;
        padding: 1rem 1.2rem;
        border-radius: 4px;
        white-space: pre-wrap;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .stButton>button {
        background-color: #7c3aed;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 4px;
        font-size: 1rem;
    }
    .stButton>button:hover { background-color: #5b21b6; }
</style>
""", unsafe_allow_html=True)

TOOLS = {
    "🎨 テキストから画像生成": "image_gen",
    "🔍 画像分析": "image_analyze",
    "✨ プロンプト提案": "prompt_suggest",
    "🖼️ 画像編集プロンプト": "image_edit",
}

with st.sidebar:
    st.markdown("## 🎨 AI 画像生成ツール")
    st.markdown("---")
    selected_label = st.radio("ツールを選択", list(TOOLS.keys()), label_visibility="collapsed")
    st.markdown("---")

    with st.expander("🔑 APIキー設定", expanded=False):
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help=".envファイルに GEMINI_API_KEY=your_key を記述しても設定できます",
        )
        if api_key_input:
            set_session_api_key(api_key_input)
            st.success("APIキーをセットしました")

    st.markdown("---")
    st.caption("Powered by Google Gemini / Imagen 3")

selected = TOOLS[selected_label]


def run_with_spinner(func, *args):
    with st.spinner("処理中..."):
        try:
            return func(*args)
        except ValueError as e:
            st.error(str(e))
            return None
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            return None


def show_text_result(result: str):
    if result:
        st.markdown("### 結果")
        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
        st.download_button("📥 テキストをダウンロード", result, file_name="result.txt", mime="text/plain")


def image_to_bytes(img) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── テキストから画像生成 ─────────────────────────────────
if selected == "image_gen":
    st.markdown('<div class="main-title">🎨 テキストから画像生成</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">プロンプトを入力して、Imagen 3 で高品質な画像を生成します</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area(
            "プロンプト（英語推奨）*",
            height=120,
            placeholder="例: A serene Japanese garden at sunset with cherry blossoms, photorealistic, golden hour lighting",
        )
        negative_prompt = st.text_input(
            "ネガティブプロンプト（除外したい要素）",
            placeholder="例: blurry, low quality, distorted",
        )
    with col2:
        model_label = st.selectbox(
            "画像生成モデル",
            list(AVAILABLE_IMAGE_MODELS.keys()),
            help="使用するImagenモデルを選択します",
        )
        selected_model = AVAILABLE_IMAGE_MODELS[model_label]
        aspect_ratio = st.selectbox(
            "アスペクト比",
            ["1:1", "16:9", "9:16", "4:3", "3:4"],
            help="1:1=正方形, 16:9=横長, 9:16=縦長（スマホ）",
        )
        num_images = st.slider("生成枚数", 1, 4, 1)

        st.markdown("**スタイルプリセット**")
        style_preset = st.selectbox(
            "スタイルを追加",
            [
                "なし",
                "写真リアル (photorealistic)",
                "アニメ (anime style)",
                "水彩画 (watercolor)",
                "油絵 (oil painting)",
                "デジタルアート (digital art)",
                "スケッチ (pencil sketch)",
                "ピクセルアート (pixel art)",
                "3Dレンダリング (3D render, CGI)",
            ],
        )

    STYLE_SUFFIXES = {
        "なし": "",
        "写真リアル (photorealistic)": ", photorealistic, ultra detailed, 8k",
        "アニメ (anime style)": ", anime style, vibrant colors, studio ghibli",
        "水彩画 (watercolor)": ", watercolor painting, soft colors, artistic",
        "油絵 (oil painting)": ", oil painting, textured brushstrokes, classical art",
        "デジタルアート (digital art)": ", digital art, concept art, artstation",
        "スケッチ (pencil sketch)": ", pencil sketch, hand-drawn, black and white",
        "ピクセルアート (pixel art)": ", pixel art, 16-bit, retro game style",
        "3Dレンダリング (3D render, CGI)": ", 3D render, CGI, octane render, cinematic",
    }

    if st.button("画像を生成する", use_container_width=True):
        if not prompt:
            st.warning("プロンプトを入力してください")
        else:
            final_prompt = prompt + STYLE_SUFFIXES.get(style_preset, "")
            st.caption(f"使用プロンプト: {final_prompt}")
            st.caption(f"使用モデル: {selected_model}")
            images = run_with_spinner(generate_images, final_prompt, aspect_ratio, num_images, negative_prompt, selected_model)
            if images:
                st.markdown("### 生成画像")
                cols = st.columns(len(images))
                for i, (col, img) in enumerate(zip(cols, images)):
                    with col:
                        st.image(img, use_container_width=True)
                        img_bytes = image_to_bytes(img)
                        st.download_button(
                            f"📥 画像{i+1}をダウンロード",
                            img_bytes,
                            file_name=f"generated_{i+1}.png",
                            mime="image/png",
                            key=f"dl_{i}",
                        )

# ── 画像分析 ─────────────────────────────────────────────
elif selected == "image_analyze":
    st.markdown('<div class="main-title">🔍 画像分析</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">画像をアップロードして、AIによる詳細な分析・説明を生成します</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "画像をアップロード *",
        type=["jpg", "jpeg", "png", "webp"],
        help="JPG, PNG, WebP形式に対応",
    )

    analysis_type = st.selectbox("分析タイプ", list(ANALYSIS_PROMPTS.keys()))

    if uploaded_file:
        st.image(uploaded_file, caption="アップロード画像", use_container_width=False, width=400)

    if st.button("分析する", use_container_width=False):
        if not uploaded_file:
            st.warning("画像をアップロードしてください")
        else:
            image_bytes = uploaded_file.read()
            result = run_with_spinner(analyze_image, image_bytes, analysis_type)
            show_text_result(result)

# ── プロンプト提案 ───────────────────────────────────────
elif selected == "prompt_suggest":
    st.markdown('<div class="main-title">✨ プロンプト提案</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">テーマとスタイルを入力して、画像生成用プロンプトを複数提案します</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        theme = st.text_input(
            "テーマ *",
            placeholder="例: 未来都市の夜景、かわいいロボット、幻想的な森",
        )
        count = st.slider("提案数", 3, 10, 5)
    with col2:
        style = st.selectbox(
            "スタイル",
            [
                "写真リアル",
                "アニメ・イラスト",
                "水彩・アート",
                "ファンタジー",
                "サイバーパンク",
                "ミニマリスト",
                "ポップアート",
                "ヴィンテージ・レトロ",
                "モノクロ",
            ],
        )

    if st.button("プロンプトを提案する", use_container_width=False):
        if not theme:
            st.warning("テーマを入力してください")
        else:
            result = run_with_spinner(suggest_prompts, theme, style, count)
            show_text_result(result)

# ── 画像編集プロンプト ───────────────────────────────────
elif selected == "image_edit":
    st.markdown('<div class="main-title">🖼️ 画像編集プロンプト</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">既存の画像と編集指示から、新しい画像生成プロンプトを作成します</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "元画像をアップロード *",
        type=["jpg", "jpeg", "png", "webp"],
    )

    edit_instruction = st.text_area(
        "編集指示 *",
        height=100,
        placeholder="例: 背景を宇宙に変えて、全体をサイバーパンクな雰囲気にしてください",
    )

    if uploaded_file:
        st.image(uploaded_file, caption="元画像", use_container_width=False, width=400)

    if st.button("編集プロンプトを生成する", use_container_width=False):
        if not uploaded_file or not edit_instruction:
            st.warning("画像と編集指示を入力してください")
        else:
            image_bytes = uploaded_file.read()
            result = run_with_spinner(create_edit_prompt, image_bytes, edit_instruction)
            if result:
                show_text_result(result)
                st.info("💡 上記のプロンプトを「テキストから画像生成」タブに貼り付けて、新しい画像を生成できます。")
