[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sprout-mr-eo-ethiopia.streamlit.app)

# 🌱 Project SPROUT: MR-EO Ethiopia
**Multi-Risk Earth Observation & Carbon Modeling for Ethiopia**

A GeoAI proposal and technical implementation for **Life eCOadapt50**. This project uses 100% open-source Earth Observation data (Sentinel-1, Sentinel-2, GEDI) to map land cover and estimate above-ground carbon biomass using Self-Supervised Learning (SSL) and PyTorch regression models.

## 🚀 Features
*   **PyTorch Deep Learning:** Custom SSL weights (`gamo_gofa_ssl_weights.pth`) and carbon regression models.
*   **Data Fusion:** Integration of 12-band optical and SAR data.
*   **Automated Mapping:** Scripts to generate publication-ready maps.
*   **Interactive Dashboard:** Built with Streamlit to visualize outputs and model architectures.

## 📂 Repository Structure
*   `app.py` - The Streamlit dashboard application.
*   `*.py` - Python scripts for data acquisition, training, inference, and mapping.
*   `reports/` - Deliverables including the `Open_Data_Menu.md`.
*   `*.png` - Publication-ready figures and maps.

## 💻 How to Run Locally
1. Clone this repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.\.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the dashboard: `streamlit run app.py`

## 🌍 The 7-Step GeoAI Workflow
This project aligns with the *Project SPROUT* proposal, mapping open satellite data to co-created, decision-ready climate adaptation tools.