from importlib.resources import files
from pathlib import Path

TAXI_CSV_PATH = Path(__file__).resolve().parents[1] / "data"

DATA_PATH = Path(__file__).parents[1] / "data"

MODELS_PATH = Path(__file__).parents[1] / "models"
RF_PATH = MODELS_PATH / "taxi_rf_model.joblib"

ASSETS_PATH = Path(__file__).parents[1] / "assets"
IMG_PATH = ASSETS_PATH / "taxi_bild.jpg"

