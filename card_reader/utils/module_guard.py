import functools
import importlib


def requires_module(module_name):
    """Decorator to disable a function if the module is missing."""

    def decorator(func):
        try:
            importlib.import_module(module_name)
            module_available = True
        except ModuleNotFoundError:
            module_available = False

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not module_available:
                try:
                    import streamlit as st

                    st.warning(f"⚠️ '{func.__name__}' disabled: missing '{module_name}'")
                except ImportError:
                    print(f"⚠️ '{func.__name__}' disabled: missing '{module_name}'")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator
