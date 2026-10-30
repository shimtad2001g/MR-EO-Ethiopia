# 🌱 Project SPROUT: Stakeholder Guide
**Prepared for:** The Life eCOadapt50 Initiative
**Project Lead:** Shimeles Tadesse Zelelew
**Live Dashboard:** [https://sprout-mr-eo-ethiopia.streamlit.app](https://sprout-mr-eo-ethiopia.streamlit.app)

---

## 🎯 Executive Summary
**Project SPROUT** (Multi-Risk Earth Observation & Carbon Modeling) is a decision-ready, open-source GeoAI tool designed to support climate adaptation strategies in Ethiopia. By integrating Sentinel-1, Sentinel-2, and GEDI satellite data, this project provides high-resolution land cover mapping and above-ground carbon biomass estimates for the Gamo Gofa region.

This dashboard serves as the visualization layer for a **7-Step GeoAI Workflow**, transforming raw satellite data into actionable insights for climate resilience.

---

## 🗺️ How to Use the Dashboard

The live dashboard is divided into three main sections designed for different stakeholders:

### 1. 📊 Project Overview
*   **Purpose:** Provides a high-level summary of the data sources and the Self-Supervised Learning (SSL) methodology used. 
*   **For Stakeholders:** Read this section to understand the scientific foundation and the open-source nature of the data used.

### 2. 🗺️ Generated Maps
*   **Purpose:** Visualizes the spatial distribution of ecological zones and land cover classifications.
*   **Interactive Map:** Users can pan, zoom, and hover over the 5 validation zones (Wurch, Dega, Weyna Dega, Kolla, and Bereha) to see specific locations.
*   **Publication Maps:** High-resolution static maps are provided for reports, presentations, and policy briefs.

### 3. 🤖 ML Models & Pipeline
*   **Purpose:** Outlines the technical architecture of the PyTorch models.
*   **Interactive Demo:** You can upload a sample Sentinel-2 image patch to simulate a carbon biomass prediction. *(Note: This is currently a simulated demo. The production model can be integrated via a FastAPI backend).*

---

## 🌍 Alignment with Climate Adaptation Goals
*   **Risk Assessment:** The 5 ecological zones mapped in the dashboard allow stakeholders to target specific climate adaptation interventions (e.g., reforestation in degraded Kolla zones, conservation in Wurch zones).
*   **Carbon Monitoring:** The SSL models provide accurate above-ground biomass estimates, essential for carbon credit verification and MRV (Measurement, Reporting, and Verification) frameworks.
*   **Open Science:** All code, data pipelines, and models are hosted publicly on GitHub, ensuring transparency and reproducibility for the Life eCOadapt50 team.

---

## 📞 Next Steps & Contact
We invite the Life eCOadapt50 team to explore the live dashboard. For technical inquiries, data access, or collaboration on model deployment, please contact:
*   **GitHub:** [@shimtad2001g](https://github.com/shimtad2001g)
