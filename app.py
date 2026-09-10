import streamlit as st
import requests
from urllib.parse import urlparse

st.set_page_config(
    page_title="TikTok Text",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .block-container {
        max-width: 520px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    h1 {
        text-align: center;
        font-size: 2rem !important;
        margin-bottom: .2rem !important;
    }
    .subtitle {
        text-align:center;
        opacity:.72;
        margin-bottom:1.2rem;
    }
    .stTextInput input {
        font-size: 17px !important;
        min-height: 52px;
        direction: ltr;
    }
    .stButton button {
        min-height: 54px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 14px;
    }
    textarea {
        font-size: 17px !important;
        line-height: 1.5 !important;
        direction: rtl;
    }
    .card {
        padding: 14px 16px;
        border-radius: 16px;
        background: rgba(128,128,128,.08);
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 TikTok → טקסט")
st.markdown('<div class="subtitle">מדביקים קישור ומקבלים את תיאור הסרטון</div>', unsafe_allow_html=True)

url = st.text_input(
    "קישור לטיקטוק",
    placeholder="הדביקי כאן קישור לסרטון…",
    label_visibility="collapsed"
)

def valid_tiktok(u):
    try:
        host = urlparse(u).netloc.lower()
        return (
            host.endswith("tiktok.com")
            or host.endswith("vm.tiktok.com")
            or host.endswith("vt.tiktok.com")
        )
    except Exception:
        return False

def resolve(u):
    r = requests.get(
        u,
        allow_redirects=True,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    r.raise_for_status()
    return r.url

def extract_caption(u):
    full = resolve(u)
    r = requests.get(
        "https://www.tiktok.com/oembed",
        params={"url": full},
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    r.raise_for_status()
    data = r.json()
    return data.get("title", "").strip(), data.get("author_name", ""), full

if "caption" not in st.session_state:
    st.session_state.caption = ""

if st.button("✨ הוציאי לי את התיאור", type="primary", use_container_width=True):
    clean = url.strip()
    if not clean:
        st.warning("תדביקי קודם קישור לטיקטוק.")
    elif not valid_tiktok(clean):
        st.error("זה לא נראה כמו קישור של TikTok.")
    else:
        try:
            with st.spinner("שולפת..."):
                caption, author, full = extract_caption(clean)
            st.session_state.caption = caption
            st.session_state.author = author
            st.session_state.full = full
        except Exception:
            st.session_state.caption = ""
            st.error("לא הצלחתי לקרוא את הסרטון. נסי סרטון ציבורי אחר.")

if st.session_state.get("caption"):
    st.success("מצאתי ✨")
    if st.session_state.get("author"):
        st.caption(f"יוצר/ת: {st.session_state.author}")

    st.text_area(
        "התיאור",
        st.session_state.caption,
        height=220,
        label_visibility="collapsed"
    )

    safe = st.session_state.caption.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    st.components.v1.html(f"""
    <button onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
        this.innerText='הועתק ✓';
        setTimeout(()=>this.innerText='📋 העתקי את הטקסט',1400);
    }})"
    style="
      width:100%;
      min-height:54px;
      border:none;
      border-radius:14px;
      font-size:18px;
      font-weight:700;
      cursor:pointer;
      background:#111;
      color:white;
      font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      📋 העתקי את הטקסט
    </button>
    """, height=70)

st.markdown("---")
st.caption("שומרת רק את התיאור הציבורי של הסרטון. לא מורידה את הסרטון ולא דורשת כניסה לחשבון.")
