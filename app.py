import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
import io
import textwrap
from streamlit_oauth import OAuth2Component

# --- Page Setup ---
st.set_page_config(page_title="AI Poster Maker", layout="centered")
st.title("🎨 AI Meme & Poster Creator")
REDIRECT_URI = "https://AIMeme&PosterCreator.streamlit.app" 

try:
    CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]
except KeyError:
    st.error("⚠️ Google Secrets are missing! Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your secrets.toml or Streamlit Cloud dashboard.")
    st.stop()

# Create the Google Login component
oauth2 = OAuth2Component(
    CLIENT_ID, 
    CLIENT_SECRET, 
    "https://accounts.google.com/o/oauth2/v2/auth", 
    "https://oauth2.googleapis.com/token", 
    "https://oauth2.googleapis.com/token", 
    "https://revoke.googleapis.com/revoke"
)

# ==========================================
# 3. LOGIN SYSTEM LOGIC
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def login_screen():
    # Hide sidebar on login screen
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔒 Welcome!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #aaaaaa;'>Please log in to create AI posters.</p>", unsafe_allow_html=True)
        st.write("")
        
        # This generates the actual "Login with Google" button
        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.vn/images/branding/googleg/1x/googleg_standard_color_128dp.png",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_login",
            use_container_width=True
        )
        
        if result and "token" in result:
            st.session_state["logged_in"] = True
            st.session_state["username"] = "Google User" # They are successfully authenticated!
            st.rerun()

# ENFORCE LOGIN: Stop the app if not logged in
if not st.session_state["logged_in"]:
    login_screen()
    st.stop()
    st.header("Settings")
    # --- Sidebar for Settings ---
    with st.sidebar:
        st.header("Settings")
        design_type = st.selectbox("Design Type", ["Meme", "Event Poster", "Social Media Slogan"])
        #New : AI Tone Selector
        ai_tone = st.selectbox("AI Tone", [
            "Funny & Humorous", 
            "Sarcastic & Snarky", 
            "Professional & Clean", 
            "Inspirational & Epic",
            "Gen-Z Slang"
        ])
        
        font_style = st.selectbox("Typography Style", [
            "Meme (Impact, Thick Outline)", 
            "Modern (Clean, Bold)", 
            "Elegant (Serif, Classy)"
        ])
        
        # NEW: Text Color Picker
        text_color = st.color_picker("Text Color", "#FFFFFF") # Defaults to White
    
    # --- ANIMATED BACKGROUND, TITLE & CUSTOM FONT CODE ---
    page_bg_css = """
    <style>
    /* 1. IMPORT GOOGLE FONT */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Apply font to EVERYTHING in the app */
    /* Apply font SAFELY without breaking Streamlit icons */
    html, body, h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown {
        font-family: 'Roboto', sans-serif;
    }
    
    /* Force restore the Material Icon font just in case */
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
    }
    
    /* 2. Dark animated background */
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
    
    /* 3. Standard text color for the rest of the app */
    h2, h3, p, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* 4. DROP-IN TITLE ANIMATION */
    h1 {
        color: #ffffff !important; 
        animation: dropIn 1s cubic-bezier(0.25, 1, 0.5, 1) forwards; 
    }
    
    @keyframes dropIn {
        0% {
            opacity: 0;
            transform: translateY(-80px); 
        }
        60% {
            opacity: 1;
            transform: translateY(10px); 
        }
        80% {
            transform: translateY(-5px); 
        }
        100% {
            opacity: 1;
            transform: translateY(0); 
        }
    }
    
    /* 5. Match upload box to dark theme */
    [data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.2);
    }
    </style>
    """
    st.markdown(page_bg_css, unsafe_allow_html=True)
    # --------------------------------
    # --- Main Interface ---
    st.write("Upload a background, tell the AI what the event or joke is about, and let it generate the perfect overlay!")
    
    uploaded_file = st.file_uploader("1. Upload a background image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    topic = st.text_input("2. What is this about?", placeholder="e.g., Surviving finals week on 2 hours of sleep")
    
    if st.button("Generate & Create"):
        if not uploaded_file:
            st.error("Please upload an image first!")
        elif not topic:
            st.error("Please provide a topic for the AI!")
        else:
            with st.spinner("Generating AI caption and rendering image..."):
                try:
                    # 1. Generate Caption using Gemini
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"Write a short, catchy, and punchy {design_type} text overlay about: {topic}. The tone of the text MUST BE: {ai_tone}. Return strictly the text, no quotes or extra formatting."
                    
                    response = model.generate_content(prompt)
                    prompt = f"Write a short, catchy, and punchy {design_type} text overlay about: {topic}. Return strictly the text, no quotes or extra formatting."
                    response = model.generate_content(prompt)
                    ai_text = response.text.strip().upper() if "Meme" in font_style else response.text.strip()
                    
                    # 2. Process Image with Pillow
                    image = Image.open(uploaded_file).convert("RGBA")
                    draw = ImageDraw.Draw(image)
                    
                    # Dynamically size the font based on the image height
                    font_size = int(image.height * 0.08)
                    
                    # Map the user's selection to the correct font file
                    font_mapping = {
                        "Meme (Impact, Thick Outline)": "impact.ttf",
                        "Modern (Clean, Bold)": "roboto.ttf",
                        "Elegant (Serif, Classy)": "playfair.ttf"
                    }
                    selected_font_file = font_mapping[font_style]
    
                    try:
                        font = ImageFont.truetype(selected_font_file, size=font_size) 
                    except IOError:
                        st.warning(f"Font file '{selected_font_file}' not found. Falling back to default. Did you upload it to your repo?")
                        font = ImageFont.load_default()
    
                    # 3. Text Wrapping and Centering Logic
                    char_width = font.getlength("A") if hasattr(font, 'getlength') else 10
                    max_width_chars = int((image.width * 0.9) / char_width) 
                    wrapped_text = textwrap.wrap(ai_text, width=max_width_chars)
                    
                    current_h = image.height * 0.75 
                    
                    for line in wrapped_text:
                        bbox = draw.textbbox((0, 0), line, font=font)
                        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                        x = (image.width - w) / 2
                        
                        shadow_offset = int(font_size * 0.06)
                        
                        # --- CONDITIONAL STYLING & COLOR ---
                        if "Meme" in font_style:
                            # Meme Style: Drop shadow + thick stroke
                            draw.text((x + shadow_offset, current_h + shadow_offset), line, font=font, fill=(0, 0, 0, 200))
                            draw.text((x, current_h), line, font=font, fill=text_color, stroke_width=int(font_size * 0.05), stroke_fill="black")
                        else:
                            # Modern/Elegant Style: Soft drop shadow, NO thick stroke for a cleaner look
                            draw.text((x + (shadow_offset//2), current_h + (shadow_offset//2)), line, font=font, fill=(0, 0, 0, 150))
                            draw.text((x, current_h), line, font=font, fill=text_color)
                        
                        current_h += h + 15
    
                    # 4. Display the Result
                    st.success(f"**AI Generated Caption:** {ai_text}")
                    st.image(image, caption="Your Generated Design", use_container_width=True)
                    
                    # 5. Prepare Image for Download
                    buf = io.BytesIO()
                    final_image = image.convert("RGB")
                    final_image.save(buf, format="JPEG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download Design",
                        data=byte_im,
                        file_name="ai_generated_poster.jpg",
                        mime="image/jpeg"
                    )
                    
                except Exception as e:
    
                    st.error(f"An error occurred: {e}")
    
    







