import importlib.util

OPTIONAL_EXTRAS = {
    "torch": "ml",
    "torchvision": "ml",
    "transformers": "ml",
    "ultralytics": "cv",
    "easyocr": "ocr",
}


def check_extras(print_status=True):
    status = {}
    for pkg, extra in OPTIONAL_EXTRAS.items():
        installed = importlib.util.find_spec(pkg) is not None
        status[pkg] = installed
        if print_status:
            print(
                f"{pkg}: {'✅ installed' if installed else f'⚠️ not installed (pip install threadzip[{extra}])'}"
            )
    return status
