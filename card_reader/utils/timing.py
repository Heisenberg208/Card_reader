import time
from datetime import datetime
from functools import wraps
from utils.logger import logThis
import streamlit as st

# Dictionary to store timing data

timing_data = {}


# Decorator for timing functions
def time_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        function_name = func.__name__

        # Log timing data
        logThis.info(
            f"{function_name} took {elapsed_time:.4f} seconds", extra={"color": "cyan"}
        )

        # Store timing data in global dictionary
        if function_name not in timing_data:
            timing_data[function_name] = []
        timing_data[function_name].append(elapsed_time)

        # Also store in session state for UI access
        if "timing_data" not in st.session_state:
            st.session_state.timing_data = {}
        if function_name not in st.session_state.timing_data:
            st.session_state.timing_data[function_name] = []
        st.session_state.timing_data[function_name].append(elapsed_time)

        return result

    return wrapper


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        # Get the first argument which should be st_instance in most functions
        if args and hasattr(args[0], "session_state"):
            st_instance = args[0]

            # Initialize timing dictionary if it doesn't exist
            if "timing_metrics" not in st_instance.session_state:
                st_instance.session_state.timing_metrics = {}

            # Store the timing data
            function_name = func.__name__
            st_instance.session_state.timing_metrics[function_name] = {
                "last_execution": execution_time,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Log the execution time
            logThis.info(
                f"Function {function_name} executed in {execution_time:.4f} seconds",
                extra={"color": "cyan"},
            )
        else:
            logThis.info(
                f"Function {func.__name__} executed in {execution_time:.4f} seconds",
                extra={"color": "cyan"},
            )

        return result

    return wrapper
