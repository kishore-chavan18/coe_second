import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
from rembg import remove
import numpy as np
import cv2
from io import BytesIO

st.set_page_config(
    page_title="AI Passport Photo Studio",
    page_icon="📸",
    layout="wide"
)

st.title("📸 AI Passport Photo Studio")
st.write(
    "Upload a photo and automatically remove the background, "
    "replace it with white or black, and enhance the image like a studio portrait."
)

# -----------------------------------
# Helper Functions
# -----------------------------------

def enhance_face(image_pil):
    """
    Enhance image sharpness, brightness and clarity
    """

    # Sharpen
    sharp = ImageEnhance.Sharpness(image_pil).enhance(2.0)

    # Contrast
    contrast = ImageEnhance.Contrast(sharp).enhance(1.15)

    # Brightness
    bright = ImageEnhance.Brightness(contrast).enhance(1.05)

    return bright


def remove_background(image):
    """
    AI background removal
    """
    output = remove(image)
    return output


def add_background(foreground_pil, bg_color="white"):
    """
    Add white or black background
    """

    foreground = foreground_pil.convert("RGBA")

    if bg_color == "white":
        background = Image.new("RGBA", foreground.size, (255, 255, 255, 255))
    else:
        background = Image.new("RGBA", foreground.size, (0, 0, 0, 255))

    combined = Image.alpha_composite(background, foreground)

    return combined.convert("RGB")


def studio_enhance(image_pil):
    """
    Studio-quality enhancement
    """

    img = np.array(image_pil)

    # Convert RGB to BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Bilateral filter preserves face details
    img = cv2.bilateralFilter(img, 9, 75, 75)

    # Mild skin smoothing
    smooth = cv2.detailEnhance(img, sigma_s=10, sigma_r=0.15)

    # Convert back
    smooth = cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB)

    pil_img = Image.fromarray(smooth)

    # Final enhancements
    pil_img = enhance_face(pil_img)

    return pil_img


def image_download_bytes(image_pil):
    """
    Convert image to downloadable bytes
    """

    buf = BytesIO()
    image_pil.save(buf, format="PNG")
    byte_im = buf.getvalue()

    return byte_im


# -----------------------------------
# Sidebar Controls
# -----------------------------------

st.sidebar.header("⚙ Settings")

bg_choice = st.sidebar.selectbox(
    "Background Color",
    ["White", "Black"]
)

resize_option = st.sidebar.checkbox(
    "Resize to Passport Photo Size",
    value=True
)

# -----------------------------------
# Upload Section
# -----------------------------------

uploaded_file = st.file_uploader(
    "Upload Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    original_image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(original_image, use_container_width=True)

    if st.button("✨ Generate Studio Passport Photo"):

        with st.spinner("Processing image with AI..."):

            # Remove background
            transparent = remove_background(original_image)

            # Studio enhancement
            enhanced = studio_enhance(transparent.convert("RGB"))

            # Preserve alpha channel from transparent image
            enhanced_rgba = enhanced.convert("RGBA")
            transparent_alpha = transparent.getchannel("A")
            enhanced_rgba.putalpha(transparent_alpha)

            # Add selected background
            final_image = add_background(
                enhanced_rgba,
                bg_choice.lower()
            )

            # Resize to passport style
            if resize_option:
                final_image = final_image.resize((600, 750))

            with col2:
                st.subheader("Studio Passport Result")
                st.image(final_image, use_container_width=True)

            # Download
            img_bytes = image_download_bytes(final_image)

            st.success("Passport photo generated successfully!")

            st.download_button(
                label="⬇ Download Passport Photo",
                data=img_bytes,
                file_name="passport_photo.png",
                mime="image/png"
            )

# -----------------------------------
# Footer
# -----------------------------------

st.markdown("---")
st.caption("Built with Streamlit + AI Background Removal")
