# profanity_utils.py

import streamlit as st
from better_profanity import profanity
from profanity_hinglish import contains_hinglish_profanity


class ProfanityError(ValueError):
    """Custom error for profanity detection."""

    pass


# Load profanity dictionary once (not on every function call)
if not profanity.CENSOR_WORDSET:
    profanity.load_censor_words()


def filter_profanity_from_query(query: str, mode: str = "ui") -> str:
    """
    Filter English and Hinglish profanity from search queries.

    Args:
        query (str): The input query.
        mode (str): 'ui' (default) for Streamlit; 'api' for Flask endpoint.

    Returns:
        str: The original query if clean.

    Raises:
        ProfanityError: If inappropriate words are detected in 'api' mode.
    """
    if not query or not isinstance(query, str):
        if mode == "api":
            raise ProfanityError("Query must be a non-empty string.")
        else:
            st.warning("Please enter a valid query.")
            st.stop()

    # Normalize input for consistency
    clean_query = query.strip().lower()

    # Check for profanity (English + Hinglish)
    has_profanity = profanity.contains_profanity(
        clean_query
    ) or contains_hinglish_profanity(clean_query)

    if has_profanity:
        message = "🚫 Search query contains inappropriate language."
        if mode == "ui":
            st.warning(f"{message} Please rephrase your search.")
            st.stop()
        elif mode == "api":
            raise ProfanityError(message)

    return query  # return original unmodified query
