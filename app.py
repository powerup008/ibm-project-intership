import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import io
import textwrap

# ==========================================
# 1. PAGE SETUP & SESSION STATE
# ==========================================
st.set_page_config(page_title="AI Poster Maker", layout="centered")

# Initialize session states for login and saving the AI text
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "ai_text" not in st.session_state:
    st.session_state["ai_text"] = "" # Saves the text so sliders don't reset it!

# ==========================================
# 2. LOGIN SYSTEM LOGIC
# ==========================================
def login_screen():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔒 Welcome!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #aaaaaa;'>Please enter a nickname to start creating.</p>", unsafe_allow_html=True)
        st.write("")
        
        with st.form("login_form"):
            username = st.text_input("Choose a Username", placeholder="e.g., GuestUser")
            password = st.text_input("Enter any Password", type="password", placeholder="••••••••")
            submit_button = st.form_submit_button("Enter App", use_container_width=True)
            
            if submit_button:
                if username.strip() != "" and password.strip() != "":
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username.strip()
                    st.rerun()
                else:
                    st.error("😕 Please type a username and password to continue.")

if not st.session_state["logged_in"]:
    login_screen()
    st.stop()

# ==========================================
# 3. MAIN APP
# ==========================================

st.title("🎨 AI Meme & Poster Creator")

# --- CSS Background & Fonts ---
page_bg_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;600;700&display=swap');

html, body, h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown { font-family: 'Roboto', sans-serif; }
.material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
.stApp {
    background: linear-gradient(-45deg, #000000, #1a1a1a, #2b2b2b, #0a0a0a);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
h1 { color: #ffffff !important; animation: dropIn 1s cubic-bezier(0.25, 1, 0.5, 1) forwards; }
@keyframes dropIn {
    0% { opacity: 0; transform: translateY(-80px); }
    60% { opacity: 1; transform: translateY(10px); }
    80% { transform: translateY(-5px); }
    100% { opacity: 1; transform: translateY(0); }
}
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.2);
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

# --- Sidebar Controls ---
with st.sidebar:
    st.success(f"👤 Logged in as: **{st.session_state['username']}**")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.session_state["ai_text"] = "" # Clear text on logout
        st.rerun()
        
    st.header("⚙️ AI Settings")
    design_type = st.selectbox("Design Type", ["Meme", "Event Poster", "Social Media Slogan"])
    ai_tone = st.selectbox("AI Tone", ["Funny & Humorous", "Sarcastic & Snarky", "Professional & Clean", "Inspirational & Epic", "Gen-Z Slang"])
    
    st.header("🎨 Design Controls")
    font_style = st.selectbox("Typography Style", ["Meme (Impact, Thick Outline)", "Modern (Clean, Bold)", "Elegant (Serif, Classy)"])
    text_color = st.color_picker("Text Color", "#FFFFFF")
    
    # NEW: Sliders for Positioning and Size
    st.subheader("📍 Text Position & Size")
    x_pos = st.slider("↔️ Horizontal Position (%)", min_value=0, max_value=100, value=50, help="0 = Left edge, 50 = Center, 100 = Right edge")
    y_pos = st.slider("↕️ Vertical Position (%)", min_value=0, max_value=100, value=75, help="0 = Top, 100 = Bottom")
    text_size = st.slider("🔠 Text Size", min_value=1, max_value=20, value=8, help="Changes how large the font is relative to the image")
    # This adds a horizontal line to separate the settings from the reset
    st.divider() 
    if st.button("🔄 Reset App", use_container_width=True):
        # Clear the saved AI text from the session
        st.session_state["ai_text"] = ""
        # Rerun the app to refresh the screen
        st.rerun()

# --- Interface ---
st.write("Upload a background, tell the AI what it's about, and click Generate. Then use the sidebar to move the text!")

uploaded_file = st.file_uploader("1. Upload a background image (JPG/PNG)", type=["jpg", "jpeg", "png"])
topic = st.text_input("2. What is this about?", placeholder="e.g., Surviving finals week on 2 hours of sleep")

# Trigger Gemini AI
if st.button("✨ Generate AI Caption"):
    if not uploaded_file:
        st.error("Please upload an image first!")
    elif not topic:
        st.error("Please provide a topic for the AI!")
    else:
        with st.spinner("Writing the perfect caption..."):
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"Write a short, catchy, and punchy {design_type} text overlay about: {topic}. The tone MUST BE: {ai_tone}. Return strictly the text, no quotes or extra formatting."
                response = model.generate_content(prompt)
                
                # Save the text into memory so it doesn't disappear when you move a slider!
                st.session_state["ai_text"] = response.text.strip().upper() if "Meme" in font_style else response.text.strip()
            except Exception as e:
                st.error(f"API Error: {e}")

# Render the Image (This runs instantly every time you move a slider)
if uploaded_file and st.session_state["ai_text"]:
    try:
        image = Image.open(uploaded_file).convert("RGBA")
        draw = ImageDraw.Draw(image)
        
        # Calculate size based on the new Size Slider
        font_size = int(image.height * (text_size / 100.0))
        
        font_mapping = {
            "Meme (Impact, Thick Outline)": "impact.ttf",
            "Modern (Clean, Bold)": "roboto.ttf",
            "Elegant (Serif, Classy)": "playfair.ttf"
        }
        selected_font_file = font_mapping[font_style]

        try:
            font = ImageFont.truetype(selected_font_file, size=font_size) 
        except IOError:
            font = ImageFont.load_default()

        # Wrap text
        char_width = font.getlength("A") if hasattr(font, 'getlength') else 10
        max_width_chars = int((image.width * 0.9) / char_width) 
        wrapped_text = textwrap.wrap(st.session_state["ai_text"], width=max_width_chars)
        
        # NEW: Start height is now controlled by the Vertical Slider
        current_h = image.height * (y_pos / 100.0) 
        
        for line in wrapped_text:
            bbox = draw.textbbox((0, 0), line, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            
            # NEW: X position is now controlled by the Horizontal Slider
            x = (image.width - w) * (x_pos / 100.0)
            
            shadow_offset = int(font_size * 0.06)
            
            if "Meme" in font_style:
                draw.text((x + shadow_offset, current_h + shadow_offset), line, font=font, fill=(0, 0, 0, 200))
                draw.text((x, current_h), line, font=font, fill=text_color, stroke_width=int(font_size * 0.05), stroke_fill="black")
            else:
                draw.text((x + (shadow_offset//2), current_h + (shadow_offset//2)), line, font=font, fill=(0, 0, 0, 150))
                draw.text((x, current_h), line, font=font, fill=text_color)
            
            current_h += h + 15

        st.success(f"**AI Generated Caption:** {st.session_state['ai_text']}")
        st.image(image, caption="Your Generated Design", use_container_width=True)
        
        # Prepare Image for Download
        buf = io.BytesIO()
        final_image = image.convert("RGB")
        final_image.save(buf, format="JPEG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download Final Design",
            data=byte_im,
            file_name="ai_custom_poster.jpg",
            mime="image/jpeg"
        )
        
    except Exception as e:
        st.error(f"Image processing error: {e}")



