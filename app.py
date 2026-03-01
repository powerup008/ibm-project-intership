import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import io
import textwrap

# ==========================================
# 1. PAGE SETUP & SESSION STATE
# ==========================================
st.set_page_config(page_title="AI Poster Maker", page_icon="🎨", layout="centered")

# Initialize session state variables cleanly
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.ai_caption = ""

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def generate_caption(topic, design_type, tone):
    """Fetches a caption from the Gemini API."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = (f"Write a short, catchy, and punchy {design_type} text overlay about: {topic}. "
              f"The tone MUST BE: {tone}. Return strictly the text, no quotes or extra formatting.")
    
    response = model.generate_content(prompt)
    return response.text.strip()

def draw_text_on_image(image_file, text, font_style, text_color, x_pct, y_pct, size_pct):
    """Handles all Pillow image manipulation to keep the main UI code clean."""
    image = Image.open(image_file).convert("RGBA")
    draw = ImageDraw.Draw(image)
    
    # Font setup (Note: ensure you have these .ttf files in your project folder)
    font_size = int(image.height * (size_pct / 100.0))
    font_files = {
        "Meme": "impact.ttf",
        "Modern": "roboto.ttf",
        "Elegant": "playfair.ttf"
    }
    
    try:
        font = ImageFont.truetype(font_files.get(font_style, "impact.ttf"), size=font_size)
    except IOError:
        font = ImageFont.load_default() # Fallback if font files are missing

    # Calculate text wrapping
    char_width = font.getlength("A") if hasattr(font, 'getlength') else 10
    max_chars = int((image.width * 0.9) / char_width)
    wrapped_text = textwrap.wrap(text, width=max_chars)
    
    # Calculate starting Y position
    current_y = image.height * (y_pct / 100.0)
    shadow_offset = int(font_size * 0.06)
    
    for line in wrapped_text:
        # Get line dimensions
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        # Calculate X position
        x_pos = (image.width - line_width) * (x_pct / 100.0)
        
        # Draw text with simple shadow/stroke
        if font_style == "Meme":
            # Thick black outline for memes
            draw.text((x_pos, current_y), line, font=font, fill=text_color, 
                      stroke_width=int(font_size * 0.05), stroke_fill="black")
        else:
            # Soft drop shadow for modern/elegant
            draw.text((x_pos + shadow_offset, current_y + shadow_offset), line, 
                      font=font, fill=(0, 0, 0, 150))
            draw.text((x_pos, current_y), line, font=font, fill=text_color)
        
        current_y += line_height + 15
        
    return image.convert("RGB")

# ==========================================
# 3. LOGIN SCREEN
# ==========================================
def login_screen():
    st.title("🔒 Welcome to Poster Maker")
    st.write("Please enter a nickname to start creating.")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="e.g., GuestUser")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.form_submit_button("Log In"):
            if username and password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Please enter both a username and password.")

# Block access if not logged in
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ==========================================
# 4. MAIN APPLICATION
# ==========================================
st.title("🎨 AI Meme & Poster Creator")
st.write("Upload a background, describe your topic, and let the AI write your caption!")

# --- Sidebar ---
with st.sidebar:
    st.success(f"👤 Logged in as: **{st.session_state.username}**")
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.header("⚙️ Settings")
    design_type = st.selectbox("Design Type", ["Meme", "Event Poster", "Social Media Slogan"])
    ai_tone = st.selectbox("AI Tone", ["Funny & Humorous", "Sarcastic", "Professional", "Gen-Z Slang"])
    
    st.header("🎨 Design Controls")
    font_style = st.selectbox("Typography", ["Meme", "Modern", "Elegant"])
    text_color = st.color_picker("Text Color", "#FFFFFF")
    
    st.subheader("📍 Position & Size")
    x_pos = st.slider("↔️ Horizontal (%)", 0, 100, 50)
    y_pos = st.slider("↕️ Vertical (%)", 0, 100, 75)
    text_size = st.slider("🔠 Text Size", 1, 20, 8)
    
    st.divider()
    if st.button("🔄 Reset Image", use_container_width=True):
        st.session_state.ai_caption = ""
        st.rerun()

# --- Main Work Area ---
uploaded_file = st.file_uploader("1. Upload a background image", type=["jpg", "jpeg", "png"])
topic = st.text_input("2. What is this about?", placeholder="e.g., Surviving finals week on 2 hours of sleep")

# Generate Caption Button
if st.button("✨ Generate AI Caption", type="primary"):
    if not uploaded_file or not topic:
        st.warning("Please upload an image and provide a topic first.")
    else:
        with st.spinner("Writing the perfect caption..."):
            try:
                caption = generate_caption(topic, design_type, ai_tone)
                # Auto-uppercase for memes
                st.session_state.ai_caption = caption.upper() if font_style == "Meme" else caption
            except Exception as e:
                st.error(f"Failed to generate text: {e}")

# Render Final Image
if uploaded_file and st.session_state.ai_caption:
    try:
        final_image = draw_text_on_image(
            image_file=uploaded_file,
            text=st.session_state.ai_caption,
            font_style=font_style,
            text_color=text_color,
            x_pct=x_pos,
            y_pct=y_pos,
            size_pct=text_size
        )
        
        st.info(f"**Caption:** {st.session_state.ai_caption}")
        st.image(final_image, caption="Your Generated Design", use_container_width=True)
        
        # Prepare for download
        buf = io.BytesIO()
        final_image.save(buf, format="JPEG")
        
        st.download_button(
            label="⬇️ Download Final Design",
            data=buf.getvalue(),
            file_name="ai_poster.jpg",
            mime="image/jpeg",
            type="primary"
        )
        
    except Exception as e:
        st.error(f"Error drawing image: {e}")
