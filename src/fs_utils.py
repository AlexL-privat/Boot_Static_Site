import os
import shutil
from typing import Callable


def _clear_directory(path: str):
    """Remove all contents of the directory at `path` but do not remove `path` itself.

    If the directory does not exist, this is a no-op.
    """
    if not os.path.exists(path):
        return

    for name in os.listdir(path):
        full = os.path.join(path, name)
        try:
            if os.path.islink(full) or os.path.isfile(full):
                os.unlink(full)
            elif os.path.isdir(full):
                shutil.rmtree(full)
        except Exception:
            # Re-raise with more context
            raise


def copy_dir_recursive(src: str, dest: str, logger: Callable[[str], None] = print):
    """
    Recursively copy contents from `src` directory into `dest` directory.

    Behavior:
    - If `dest` exists, all of its contents are deleted first so the copy is clean.
    - All files and subdirectories under `src` are recreated under `dest`.
    - Logs each file copied via the `logger` callable.

    Args:
        src: Source directory path.
        dest: Destination directory path.
        logger: Callable that accepts a single string to log progress (defaults to `print`).

    Raises:
        FileNotFoundError: if `src` does not exist or is not a directory.
        Exception: any unexpected filesystem error is propagated.
    """
    if not os.path.exists(src) or not os.path.isdir(src):
        raise FileNotFoundError(f"Source directory not found: {src}")

    # Ensure destination exists, then clear its contents
    os.makedirs(dest, exist_ok=True)
    _clear_directory(dest)

    # Walk source tree and copy files/directories
    for root, dirs, files in os.walk(src):
        # Compute destination root corresponding to current `root`
        rel_root = os.path.relpath(root, src)
        dest_root = dest if rel_root == os.curdir else os.path.join(dest, rel_root)

        # Ensure directory exists in destination
        os.makedirs(dest_root, exist_ok=True)

        # Copy files
        for fname in files:
            src_path = os.path.join(root, fname)
            dest_path = os.path.join(dest_root, fname)
            shutil.copy2(src_path, dest_path)
            logger(f"Copied {src_path} -> {dest_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Recursively copy a source directory to a destination (clears destination first)")
    parser.add_argument("--src", default="static", help="Source directory (default: static)")
    parser.add_argument("--dest", default="public", help="Destination directory (default: public)")
    args = parser.parse_args()

    try:
        copy_dir_recursive(args.src, args.dest)
    except Exception as e:
        print(f"Error: {e}")
        raise
