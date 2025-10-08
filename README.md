# Taxikollen – ML Taxi Price Predictor & BI Uplift Tool (PoC)

_Project in Data Engineering and Object Oriented Programming with AI_
@OPA24

🚖 Taxikollen is a proof-of-concept full-stack  platform that combines **Machine Learning**, **FastAPI**, **Streamlit** and **geocoding APIs** into one interactive tool for price prediction and business intelligence insights.

## 🔎 Project Overview
Taxikollen is a prediction and insights platform for the public and for stake holders. It enables you to:

- Input travel data to compute distance via maps & geocoding
- Predict taxi prices instantly
- Explore and Analyze BI uplift scenarios and pricing opportunities

## Tech Stack
- **Python 3.11+**
- **FastAPI** (backend REST API)
- **Streamlit** (frontend dashboard)
- **uv** (dependency manager & virtual environments)
- **Geocoding APIs**

## 🚀 Getting Started

#### 1. Clone the repository
```git clone``` https://github.com/SusannaR11/taxipred-prediction-fullstack-SUSANNA-ROKKA-OPA24.git 

Navigate to project root folder:
```cd TAXIPRED-PREDICTION-FULLSTACK-SUSANNA-ROKKA-OPA24```

#### 2. Create a virtual environment (uv recommended)
```uv venv .venv```

#### 3. Activate the environment

Windows:

```.venv\Scripts\activate```

macOS/Linux:

```source .venv/bin/activate```

#### 4. Install project
- Navigate to repo root, then install:
```uv pip install -e .```

#### 5. Run backend (FastAPI)
```cd```src/taxipred/backend
```uvicorn api:app --reload```

#### 6. Launch frontend (Streamlit)
```cd```src/taxipred/frontend
```streamlit run dasboard.py```

## 🛣️ Roadmap / Future Work
Planned improvements and next steps for Taxikollen:
- **Google Maps Integration** -> interactive route mapping for trips
- **Optimized Map Funciton** -> improve stability & route visualization
- **Weather API Integration** -> real-world weather data for pricing insights
- **Trafikstyrelsend API** -> traffic data to drive predictions
- **Interactive BI Features** -> richer graphs, data-driven simulations, user trip history for business optimization
- **Dynamic Pricing Engine** -> integrate live external data (traffic + weather) to adjust fares in-app
- **Responsive Frontend** -> mobile-friendly: Streamlit/React wrapper
- **Power BI / Superset / Looker** -> advanced analytics dashboard
- **Model Optimization** -> anti-drift strategies, retraining pipelines
- **Live Geocoding Improvements** -> faster & more reliable address lookups
- **User Management & Auth** -> secure logins for stakeholders
- **Testing & CI/CD** -> integration tests, automated pipeline
- **Cloud Deployment** -> deploy on Azure/AWS/GCP for real-world usage

#### Creator:
Susanna Rokka 
GitHub: ```@SusannaR11```
