# taxipred-prediction-fullstack-SUSANNA-ROKKA-OPA24

# Taxikollen – ML Taxi Price Predictor & BI Uplift Tool (PoC)

_Project in Data Engineering and Object Oriented Programming with AI_
@OPA24

A proof-of-concept for an interactive Price Prediction and BI Analytics platform that combines ML and geocoding with an uplift engine using **FastAPI** and **Streamlit**

## Project Description
Taxikollen is a prediction and insights platform for the public and for stake holders powered by Machine Learning and . It enables you to:

- Input travel data to compute distance using maps and geocoding
- Predict price with the click of a button
- Analyze BI uplifts and pricing opportunities

## How to Run

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


#### Creator:
Susanna Rokka 
GitHub: ```@SusannaR11```
