# 🎨 AI Meme & Poster Creator

A web-based application built with Streamlit that uses Google's Gemini AI to generate catchy captions and overlays them onto user-uploaded images.

## ✨ Features
* **Simple Login System**: Session-based login to keep your workspace private.
* **AI-Powered Captions**: Uses the `gemini-2.5-flash` model to generate context-aware text based on your topic and desired tone.
* **Customizable Typography**: Choose from Meme, Modern, or Elegant font styles.
* **Live Image Editing**: Adjust text color, size, and positioning with real-time visual updates.
* **One-Click Download**: Instantly export your final design as a high-quality JPEG.

## 🛠️ Prerequisites
* Python 3.8 or higher
* A Google Gemini API Key

## 🚀 Installation & Setup

**1. Install dependencies**
Open your terminal in the project folder and install the required Python packages:
`pip install -r requirements.txt`

**2. Set up your API Key**
* Inside your project folder, create a new folder named `.streamlit`
* Inside the `.streamlit` folder, create a file named `secrets.toml`
* Add your Gemini API key to the file exactly like this:
`GEMINI_API_KEY = "your_actual_api_key_goes_here"`

**3. Add Custom Fonts (Optional but recommended)**
For the fonts to work perfectly, place `impact.ttf`, `roboto.ttf`, and `playfair.ttf` directly in your main project folder. If you skip this, the app will just use a standard default font.

## 💻 Running the App
Start the app by running this command in your terminal:
`streamlit run app.py`
