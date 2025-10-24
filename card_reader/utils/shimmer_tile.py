def get_image_aspect_ratio(image):
    """
    Get the aspect ratio of an image.

    Args:
        image: PIL Image or Streamlit uploaded file

    Returns:
        float: aspect ratio (width/height)
    """
    from PIL import Image

    # Handle different input types
    if hasattr(image, "name"):  # Streamlit uploaded file
        img = Image.open(image)
    elif isinstance(image, Image.Image):  # PIL Image
        img = image
    else:
        img = Image.open(image)

    width, height = img.size
    return width / height


# Alternative approach using CSS that mimics Streamlit's image behavior
def shimmer_tile_streamlit_style(aspect_ratio=1.0):
    """
    Create a shimmer that exactly mimics how Streamlit displays images.
    This should match the final image size perfectly.
    """
    shimmer_css = f"""
    <style>
    .st-shimmer {{
        width: 100%;
        max-width: 100%;
        position: relative;
        overflow: hidden;
        border-radius: 6px; /* Match Streamlit's default border radius */
        background: #f6f7f8;
        aspect-ratio: {aspect_ratio:.6f}; /* Modern CSS aspect-ratio */
    }}
    
    /* Fallback for browsers that don't support aspect-ratio */
    .st-shimmer.fallback {{
        aspect-ratio: auto;
    }}
    .st-shimmer.fallback::before {{
        content: "";
        display: block;
        padding-top: {(1 / aspect_ratio) * 100:.2f}%;
    }}
    
    .st-shimmer::after {{
        content: "";
        position: absolute;
        top: 0;
        left: -150px;
        height: 100%;
        width: 150px;
        background: linear-gradient(to right, transparent 0%, rgba(255,255,255,0.8) 50%, transparent 100%);
        animation: shimmer 1.5s infinite ease-in-out;
    }}
    
    @keyframes shimmer {{
        0% {{ left: -150px; }}
        100% {{ left: 100%; }}
    }}
    
    /* Match Streamlit's responsive behavior */
    @media (max-width: 768px) {{
        .st-shimmer {{
            border-radius: 4px;
        }}
    }}
    </style>
    <div class="st-shimmer"></div>
    """
    return shimmer_css


# Simple one-liner replacement for your existing code:
def shimmer_tile_auto(single_image):
    """
    Simple replacement for shimmer_tile_1() that automatically sizes to match the image.
    """
    aspect_ratio = get_image_aspect_ratio(single_image)
    return shimmer_tile_streamlit_style(aspect_ratio)
