"""Application entry point.

Run locally with:  python app.py
On Hugging Face Spaces this file is what the Gradio SDK executes.

We add ``src/`` to the path so the package imports without an install step
(Hugging Face only runs ``pip install -r requirements.txt``, not the package).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from data_analyst.ui.app import main  # noqa: E402  (after sys.path setup)

if __name__ == "__main__":
    main()
