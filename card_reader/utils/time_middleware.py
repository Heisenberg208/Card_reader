import functools
import logging
import time


# Configure logging for timing information
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("endpoint_timer")


def timeit_decorator(func):
    """
    Decorator to time specific functions
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time

        # Log timing information
        logger.info(f"FUNCTION TIMING: {func.__name__} - {elapsed_time:.4f} seconds")

        return result

    return wrapper
