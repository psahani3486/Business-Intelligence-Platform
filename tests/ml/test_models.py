import os
import sys

# Add project root to sys path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.ml.utils import get_latest_model

def test_model_loader_handles_missing_gracefully():
    # Attempting to load a non-existent model should return None and not crash
    model = get_latest_model("this_model_does_not_exist")
    assert model is None
