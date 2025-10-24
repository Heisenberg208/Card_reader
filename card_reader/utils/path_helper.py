import os
from pathlib import Path

package_root = str(Path(__file__).parent.parent)
print(f"Package root: {package_root}")


def find_project_root(parent_dir, fallback=Path.cwd(), set_path=False):
    """
    Walk up the tree to find the project root.
    """
    current = Path(fallback).resolve()
    print(f"Starting directory: {current}")

    for parent in [current] + list(current.parents):
        if parent.name == parent_dir:
            print(f"Project root found by directory name: {parent}")
            if set_path:
                print("Setting cwd to project root")
                os.chdir(parent)
            return parent

    print(f"No match found. Using fallback: {current}")
    return current


# Usage
find_project_root(parent_dir="tz-script")
