from setuptools import setup
from setuptools import find_packages

# find_packages will find all the packages with __init__.py
print(find_packages())

setup(
    name="taxipred",
    version="0.0.1",
    description="this package contains taxipred app",
    author="Susanna Rokka",
    author_email="susanna.rokka@student.nbi-handelsakademin.se",
    install_requires=["streamlit", "pandas", "fastapi", "uvicorn", "numpy", "joblib", "scikit-learn", "geopy", "requests", "folium", "streamlit-option-menu", "streamlit-folium", "streamlit-geolocation"],
    include_package_data=True,
    package_dir={"": "src"},
    package_data={"taxipred": ["data/*.csv", "models/*.joblib"]},
    packages=find_packages(),
)

# uv pip install -e .
