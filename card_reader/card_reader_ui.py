import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from utils.logger import logThis
import streamlit as st
from ocr_processor import (
    load_ocr_reader,
    process_ocr_to_json,
    save_to_json,
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PIL import Image
from utils.aws_helper import upload_file_to_s3
from utils.constants import (
    ALLOWED_EXTENSIONS,
    CARD_SAMPLES,
    ENVIRONMENT,
    IMAGES_PER_ROW,
    UPLOAD_FOLDER_CARD,
    gemini_key,
)
from utils.messages import DESCRIPTION_OCR, TITLE_OCR
from werkzeug.utils import secure_filename




def display_images_with_buttons(image_paths, image_size=(200, 200)):
    if not image_paths:
        st.info("No images found.")
        return

    num_images = len(image_paths)
    rows = (num_images + IMAGES_PER_ROW - 1) // IMAGES_PER_ROW

    for row in range(rows):
        cols = st.columns(IMAGES_PER_ROW)
        for col in range(IMAGES_PER_ROW):
            idx = row * IMAGES_PER_ROW + col
            if idx < num_images:
                sample_file = image_paths[idx]

                # wrap inside one container so image+button share same element
                with cols[col].container(border=True):
                    image = Image.open(sample_file)
                    st.image(image, width="content")

                    # Compare by filename string because selected_sample stores the name
                    selected_name = st.session_state.get("selected_sample")
                    button_text = (
                        "✅ Selected"
                        if selected_name == sample_file.name
                        else f"Select:{idx + 1}"
                    )
                    button_disabled = selected_name == sample_file.name

                    if st.button(
                        button_text,
                        key=f"select_{idx}",
                        disabled=button_disabled,
                        type="secondary",
                        width="stretch",
                    ):
                        # store only the filename (string) in session state to avoid Path objects
                        st.session_state.selected_sample = sample_file.name
                        st.toast(f"✅ Image selected:{idx + 1}")
                        st.rerun()


def handle_clear_output():
    """Clear search results and reset display."""
    st.session_state.extracted_text = ""
    st.session_state.final_json = ""
    # Clear selected sample from session state
    st.session_state.selected_sample = None
    st.rerun()


def handle_image_upload_tab():
    """Handle the image upload tab functionality"""
    user_uploaded_image = st.file_uploader("Upload a Card", type=ALLOWED_EXTENSIONS)

    uploaded_image = None
    uploaded_image_name = None
    is_user_uploaded = False

    if user_uploaded_image:
        uploaded_image = user_uploaded_image
        uploaded_image_name = secure_filename(user_uploaded_image.name)
        is_user_uploaded = True

    return uploaded_image, uploaded_image_name, is_user_uploaded


def handle_sample_images_tab():
    """Handle the sample images tab functionality"""
    sample_images_dir = Path(CARD_SAMPLES)
    uploaded_image = None
    uploaded_image_name = None
    is_user_uploaded = False

    if sample_images_dir.exists():
        sample_files = [
            f.name
            for f in sample_images_dir.iterdir()
            if f.is_file() and f.suffix.lower().lstrip(".") in ALLOWED_EXTENSIONS
        ]

        if sample_files:
            sample_files = sample_files[:4]

            if st.session_state.selected_sample:
                selected_sample_path = sample_images_dir.joinpath(
                    st.session_state.selected_sample
                )
                try:
                    with open(selected_sample_path, "rb") as f:
                        image_bytes = f.read()
                    uploaded_image = io.BytesIO(image_bytes)
                    uploaded_image.name = st.session_state.selected_sample
                    uploaded_image_name = secure_filename(
                        str(st.session_state.selected_sample)
                    )
                    is_user_uploaded = False
                except Exception as e:
                    st.error(f"Error loading selected image: {str(e)}")

            st.markdown(
                """
                    <div style='text-align: center; font-weight: bold; font-style: italic; color: green;margin-bottom: 12px;'>
                        Please select a sample image and proceed
                    </div>
                    """,
                unsafe_allow_html=True,
            )
            image_paths = [sample_images_dir.joinpath(f) for f in sample_files]
            display_images_with_buttons(image_paths=image_paths)

        else:
            st.warning(f"No sample images found in '{sample_images_dir}' directory.")
    else:
        st.warning(f"Sample images directory '{sample_images_dir}' does not exist.")
        st.info(
            "To use sample images, create a 'sample_images' directory and add some business card images."
        )

    return uploaded_image, uploaded_image_name, is_user_uploaded


def handle_image_display_and_save(
    image, uploaded_image_name, is_user_uploaded, uploaded_image
):
    """Handle image display and save functionality"""
    st.subheader("Selected Image")
    st.image(
        image,
        caption=f"Business Card: {uploaded_image_name}",
        width="stretch",
    )

    # Always show button, disable if not user uploaded
    save_btn = st.button(
        "💾 Save Uploaded Image",
        disabled=not is_user_uploaded,
        help="Upload your actual images to enable Save.",
        use_container_width=True,  # modern replacement for width="stretch"
    )

    if is_user_uploaded and save_btn:
        try:
            if ENVIRONMENT == "production":
                # --- Upload to S3 ---
                s3_key = f"{UPLOAD_FOLDER_CARD}{uploaded_image_name}"

                # Reset file pointer
                if hasattr(uploaded_image, "seek"):
                    uploaded_image.seek(0)

                # Upload
                upload_success = upload_file_to_s3(uploaded_image, s3_key)

                if not upload_success:
                    st.error("❌ Failed to upload image to S3. Please try again.")
                    return None
                else:
                    st.toast("✅ Successfully uploaded image to S3 Bucket", icon="✅")

            else:
                # --- Local Save ---
                uploads_dir = Path(UPLOAD_FOLDER_CARD)
                uploads_dir.mkdir(parents=True, exist_ok=True)

                # Unique filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                saved_filename = f"card_{timestamp}_{uploaded_image_name}"
                save_path = uploads_dir / saved_filename

                # Save locally
                if hasattr(uploaded_image, "seek"):
                    uploaded_image.seek(0)
                image.save(save_path)

                st.toast("✅ Image saved")

        except Exception as e:
            st.error(f"❌ Error saving image: {str(e)}")


def handle_processing_section(image, reader):
    """Handle the main processing section"""
    st.subheader("Processing")

    # One-click OCR to JSON processing
    if st.button("🔍 Extract & Process to JSON", type="primary", width="stretch"):
        with st.spinner("Extracting text and processing with AI..."):
            try:
                json_result, extracted_text = process_ocr_to_json(
                    image, reader, gemini_key
                )

                # Store results in session state
                st.session_state.final_json = json_result
                st.session_state.extracted_text = extracted_text

                # Parse JSON to check for errors and save if successful
                try:
                    json_data = json.loads(json_result)

                    if "error" in json_data and json_data["error"]:
                        st.error(f"Processing error: {json_data['error']}")
                    else:
                        # Save to JSON file
                        if save_to_json(json_data):
                            st.toast(
                                " Business card processed successfully!",
                                icon="✅",
                            )
                        else:
                            st.warning("JSON created but failed to save to file")

                except json.JSONDecodeError:
                    st.error("Invalid JSON format returned")

            except Exception as e:
                st.error(f"Processing Error: {str(e)}")

    if st.button("🗑️ Clear Results", width="stretch"):
        handle_clear_output()


def display_results():
    """Display extracted text and final JSON results"""
    # Display extracted text in an expander (optional view)
    if st.session_state.extracted_text:
        with st.expander("📝 View Extracted Text", expanded=False):
            st.text_area(
                "Raw OCR Output:",
                value=st.session_state.extracted_text,
                height=100,
                disabled=True,
            )

    # Display final JSON result
    if st.session_state.final_json:
        st.subheader("📊 Extracted Information")

        try:
            # Parse and display JSON
            json_data = json.loads(st.session_state.final_json)
            st.json(json_data)

            # Download buttons
            col1, _ = st.columns(2)

            with col1:
                st.download_button(
                    label="💾 Download  JSON",
                    data=st.session_state.final_json,
                    file_name=f"business_card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    width="stretch",
                )

        except json.JSONDecodeError:
            st.subheader("Raw Output")
            st.code(st.session_state.final_json, language="json")
            st.warning("Output may not be valid JSON. Please check the format.")


def main():
    """Main Streamlit application function"""
    logThis.info("Currently on CARD READER", extra={"color": "blue"})
    st.title(TITLE_OCR)
    st.write(DESCRIPTION_OCR)

    # Information expander
    with st.expander("ℹ️ How this works"):
        st.markdown(
            """
        1. **Upload Image**: Choose a clear image of a business card
        2. **One-Click Processing**: Click "🔍 Extract & Process to JSON" to:
          - Extract text using OCR
          - Process with Gemini AI
          - Get structured JSON output
        3. **Download**: Get the structured information as a JSON file
        
        **Tips:**
        - Use clear, well-lit images for better OCR results
        - The app works best with standard business card layouts
        - Make sure your Gemini API key is configured in constants
        - All results are saved and appended to a JSON file
        """
        )

    # Initialize session state
    st.subheader(":green[Card Image]")
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "final_json" not in st.session_state:
        st.session_state.final_json = ""
    if "selected_sample" not in st.session_state:
        st.session_state.selected_sample = None

    # Load OCR reader
    with st.spinner("Please wait while warming up!"):
        try:
            reader = load_ocr_reader()
            if reader:
                logThis.info("Reader loaded successfully ✅")
                st.success("OCR model ready to use!")
            else:
                logThis.warning("Reader returned None ⚠️")
                st.warning("OCR reader failed to initialize.")
        except Exception as e:
            reader = None
            err_msg = f"OCR Reader initialization failed: {e}"
            logThis.error(err_msg)
            st.error("❌ Failed to load OCR reader. Check logs for details.")

    # Initialize main variables
    uploaded_image = None
    uploaded_image_name = None
    is_user_uploaded = False

    # Create tabs for upload and sample images
    upload_tab, _ = st.tabs(["📁 Upload Card", "🖼️ Sample Cards"])

    with upload_tab:
        (
            uploaded_image,
            uploaded_image_name,
            is_user_uploaded,
        ) = handle_image_upload_tab()



    # Main processing section - only show if an image is available
    if uploaded_image is not None:
        # Display the selected/uploaded image
        try:
            if hasattr(uploaded_image, "seek"):
                uploaded_image.seek(0)  # Reset file pointer for BytesIO objects
            image = Image.open(uploaded_image)
        except Exception as e:
            st.error(f"Error opening image: {str(e)}")
            return

        col1, col2 = st.columns([1, 1])

        with col1:
            handle_image_display_and_save(
                image, uploaded_image_name, is_user_uploaded, uploaded_image
            )

        with col2:
            handle_processing_section(image, reader)

        # Display results section
        display_results()


if __name__ == "__main__":
    main()
