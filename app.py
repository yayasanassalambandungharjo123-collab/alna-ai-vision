import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx
import base64
import io
from PIL import Image

# ============================================
# 🔑 API KEY GEMINI (GANTI DENGAN API KEY ANDA)
# ============================================
GEMINI_API_KEY = "AQ.Ab8RN6JlOfgYvnuo0sZY2yBb9XCy81uG-R6MEEGYBRLqWTuB0Q"
# ============================================

# Konfigurasi Gemini
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="ALNA AI Vision",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="80" height="80">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF006E"/>
      <stop offset="50%" style="stop-color:#FB5607"/>
      <stop offset="100%" style="stop-color:#FFBE0B"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="90" fill="url(#g1)"/>
  <circle cx="100" cy="100" r="70" fill="#1a1a2e" opacity="0.4"/>
  <text x="100" y="135" font-family="Arial" font-size="100" font-weight="bold" fill="white" text-anchor="middle">A</text>
  <circle cx="45" cy="55" r="6" fill="#FFBE0B"/>
  <circle cx="155" cy="55" r="6" fill="#FFBE0B"/>
  <circle cx="45" cy="145" r="6" fill="#FFBE0B"/>
  <circle cx="155" cy="145" r="6" fill="#FFBE0B"/>
</svg>
"""

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except Exception as e:
        return f"Error membaca PDF: {str(e)}"

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error membaca Word: {str(e)}"

CSS_CODE = """
<style>
    section[data-testid="stSidebar"] {
        width: 240px !important;
        min-width: 240px !important;
        max-width: 240px !important;
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4 {
        font-size: 0.85rem !important; color: white !important;
    }
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main-title {
        font-size: 3.5rem; font-weight: 900; color: white; text-align: center;
        margin: 20px 0 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle { text-align: center; color: #FFD700; font-size: 1.2rem; margin-bottom: 30px; font-weight: 500; }
    .logo-center { text-align: center; margin: 20px 0; }
    .welcome-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin: 20px 0; }
    .feature-card { background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .feature-card h4 { color: #764ba2; margin: 0 0 10px 0; font-size: 1.1rem; }
    .feature-card p { color: #4a5568; margin: 0; font-size: 0.95rem; }
    .info-box { background: linear-gradient(135deg, #FF006E 0%, #FB5607 100%); color: white; padding: 15px; border-radius: 12px; margin: 15px 0; }
    .stButton > button { background: linear-gradient(90deg, #FF006E, #FB5607); color: white; border: none; border-radius: 10px; padding: 10px; font-weight: bold; width: 100%; font-size: 0.85rem; }
    .footer { text-align: center; color: white; padding: 20px; margin-top: 40px; border-top: 2px solid rgba(255,255,255,0.3); font-size: 0.9rem; }
    div[data-testid="stChatInput"] { position: fixed; bottom: 0; left: 240px; right: 0; z-index: 100; padding: 15px 30px; background: transparent; }
    div[data-testid="stChatInput"] > div { background: rgba(255, 255, 255, 0.2); border: 2px solid rgba(255, 255, 255, 0.5); border-radius: 30px; backdrop-filter: blur(15px); box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
    div[data-testid="stChatInput"] input { background: transparent; color: white; border: none; }
    div[data-testid="stChatInput"] input::placeholder { color: rgba(255, 255, 255, 0.8); }
    .chat-row { display: flex; margin: 12px 0; width: 100%; }
    .chat-row.user { justify-content: flex-end; }
    .chat-row.assistant { justify-content: flex-start; }
    .chat-bubble { max-width: 70%; padding: 14px 20px; border-radius: 18px; font-size: 1rem; line-height: 1.5; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }
    .chat-bubble.user { background: linear-gradient(135deg, #FF006E 0%, #FB5607 100%); color: white; border-bottom-right-radius: 4px; margin-right: 10px; }
    .chat-bubble.assistant { background: rgba(255, 255, 255, 0.95); color: #1a1a2e; border-bottom-left-radius: 4px; margin-left: 10px; }
    .chat-avatar { width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
    .chat-avatar.user { background: linear-gradient(135deg, #FF006E, #FB5607); color: white; order: 2; margin-left: 10px; }
    .chat-avatar.assistant { background: linear-gradient(135deg, #667eea, #764ba2); color: white; order: 0; margin-right: 10px; }
    .bottom-spacer { height: 100px; }
    div[data-testid="stChatMessage"] { display: none !important; }
    .uploaded-file-badge { display: inline-block; background: rgba(255, 255, 255, 0.2); border: 1px solid rgba(255, 255, 255, 0.4); padding: 4px 10px; border-radius: 12px; font-size: 0.85rem; margin: 5px 0; color: white; }
</style>
"""

st.markdown(CSS_CODE, unsafe_allow_html=True)

def render_chat_bubble(role, content, is_typing=False):
    avatar_emoji = "" if role == "user" else ""
    row_class = "user" if role == "user" else "assistant"
    bubble_class = "user" if role == "user" else "assistant"
    typing_text = "🤔 *ALNA AI sedang menganalisis...* 🖼️" if is_typing else content
    html = f"""
    <div class="chat-row {row_class}">
        <div class="chat-avatar {row_class}">{avatar_emoji}</div>
        <div class="chat-bubble {bubble_class}">{typing_text}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "file_context" not in st.session_state:
    st.session_state.file_context = ""
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_name" not in st.session_state:
    st.session_state.image_name = ""

with st.sidebar:
    st.markdown(f'<div style="text-align:center">{LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown("### ️ ALNA AI Vision", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <h4 style="margin:0 0 8px 0; color:white;">✨ AI Bisa Melihat!</h4>
        <p style="margin:0; color:white;">Upload gambar, dan AI akan menganalisis isinya secara langsung.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📁 Upload File")
    uploaded_files = st.file_uploader(
        "Pilih file...",
        type=["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )
    if uploaded_files:
        file_name = uploaded_files.name
        file_ext = file_name.split(".")[-1].lower()
        st.session_state.uploaded_files = [file_name]
        if file_ext in ["png", "jpg", "jpeg"]:
            st.session_state.uploaded_image = Image.open(uploaded_files)
            st.session_state.image_name = file_name
            st.session_state.file_context = f"[User mengupload gambar: {file_name}]"
            st.image(st.session_state.uploaded_image, caption="Preview Gambar", use_container_width=True)
        elif file_ext == "pdf":
            st.session_state.file_context = f"\n--- DOKUMEN: {file_name} ---\n{extract_text_from_pdf(uploaded_files)}\n"
            st.session_state.uploaded_image = None
        elif file_ext in ["docx", "doc"]:
            st.session_state.file_context = f"\n--- DOKUMEN: {file_name} ---\n{extract_text_from_docx(uploaded_files)}\n"
            st.session_state.uploaded_image = None
        elif file_ext == "txt":
            st.session_state.file_context = f"\n--- DOKUMEN: {file_name} ---\n{uploaded_files.read().decode('utf-8')}\n"
            st.session_state.uploaded_image = None
        st.markdown(f'<span class="uploaded-file-badge">📎 {file_name}</span>', unsafe_allow_html=True)
        st.success("✅ File berhasil dimuat!")
    else:
        st.session_state.file_context = ""
        st.session_state.uploaded_image = None
        st.session_state.image_name = ""
        st.session_state.uploaded_files = []
    st.markdown("---")
    st.markdown("### ⚙️ Pengaturan")
    mode = st.radio("Pilih Mode AI:", [" Kreatif", "🎯 Akurat", "⚡ Cepat"], label_visibility="visible")
    if mode == "🎨 Kreatif":
        temperature = 0.9
    elif mode == "🎯 Akurat":
        temperature = 0.3
    else:
        temperature = 0.5
    st.markdown("---")
    if st.button("🗑️ Hapus Semua Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.uploaded_files = []
        st.session_state.file_context = ""
        st.session_state.uploaded_image = None
        st.rerun()
    st.markdown("---")
    st.markdown("### 👨‍💻 Pembuat")
    st.markdown("**Dibuat oleh:** Ikbal")
    st.markdown("**Tech:** Python + Streamlit + Gemini")
    st.markdown("**Model:** Gemini 3.8 Flash")

st.markdown(f'<div class="logo-center">{LOGO_SVG}</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">ALNA AI Vision</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Asisten Pribadi Cerdas yang Bisa Melihat & Membaca!</p>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="welcome-container">
        <div class="feature-card"><h4>️ Analisis Gambar</h4><p>"Apa yang ada di gambar ini?"</p></div>
        <div class="feature-card"><h4> Baca Teks dalam Gambar</h4><p>"Tuliskan semua teks di foto ini"</p></div>
        <div class="feature-card"><h4>📄 Rangkum Dokumen</h4><p>"Upload PDF dan minta ringkasan"</p></div>
        <div class="feature-card"><h4>💻 Coding Helper</h4><p>"Jelaskan kode Python ini"</p></div>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    render_chat_bubble(message["role"], message["content"])

if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_chat_bubble("user", prompt)
    with st.container():
        placeholder = st.empty()
        placeholder.markdown("""
        <div class="chat-row assistant">
            <div class="chat-avatar assistant">🤖</div>
            <div class="chat-bubble assistant">🤔 <i>ALNA AI sedang menganalisis...</i></div>
        </div>
        """, unsafe_allow_html=True)
        try:
            # Inisialisasi model Gemini
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": 2048,
            }
            model = genai.GenerativeModel(
                model_name="gemini-3.8-flash",
                generation_config=generation_config,
                system_instruction="Anda adalah ALNA AI Vision, asisten pribadi yang cerdas dan ramah. Anda bisa melihat gambar, membaca dokumen, dan menjawab pertanyaan dengan jelas, detail, dan membantu. Jawab dalam bahasa Indonesia kecuali diminta bahasa lain."
            )
            
            # Siapkan konten
            content_parts = []
            
            # Tambahkan gambar jika ada
            if st.session_state.uploaded_image:
                content_parts.append(st.session_state.uploaded_image)
            
            # Tambahkan konteks dokumen jika ada
            if st.session_state.file_context and st.session_state.uploaded_image is None:
                full_prompt = f"Konteks Dokumen:\n{st.session_state.file_context}\n\nPertanyaan user: {prompt}"
                content_parts.append(full_prompt)
            else:
                content_parts.append(prompt)
            
            # Kirim ke Gemini
            response = model.generate_content(content_parts)
            full_response = response.text
            
            final_html = f"""
            <div class="chat-row assistant">
                <div class="chat-avatar assistant">🤖</div>
                <div class="chat-bubble assistant">{full_response}</div>
            </div>
            """
            placeholder.markdown(final_html, unsafe_allow_html=True)
            
        except Exception as e:
            error_detail = str(e)
            error_html = f"""
            <div class="chat-row assistant">
                <div class="chat-avatar assistant">🤖</div>
                <div class="chat-bubble assistant">
                    ❌ <b>Terjadi Error:</b><br><br>
                    <code style="background:#f0f0f0; padding:10px; border-radius:8px; display:block; font-size:0.85rem; word-wrap: break-word;">
                    {error_detail}
                    </code>
                    <br>
                    <b>💡 Tips:</b> Pastikan API Key Gemini valid. Screenshot error ini jika perlu bantuan.
                </div>
            </div>
            """
            placeholder.markdown(error_html, unsafe_allow_html=True)
            full_response = f"Error: {error_detail}"
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()

st.markdown('<div class="bottom-spacer"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>👁️ <strong>ALNA AI Vision</strong> - Asisten Pribadi Cerdas</p>
    <p>Dibuat dengan ❤️ oleh Ikbal | Powered by Google Gemini</p>
    <p>© 2026 ALNA AI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
