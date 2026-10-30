import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Project SPROUT: MR-EO Ethiopia", layout="wide")

st.title("🌱 Project SPROUT: MR-EO Ethiopia - Live Dashboard")
st.markdown("**Multi-Risk Earth Observation & Carbon Modeling for Ethiopia**")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["📊 Project Overview", "🗺️ Generated Maps", "🤖 ML Models & Pipeline"])

with tab1:
    st.header("Overview")
    st.write("""
    Welcome to the MR-EO-Ethiopia dashboard. This project integrates Sentinel-2, GEDI, and Landsat data 
    to map land cover and estimate above-ground carbon biomass using Self-Supervised Learning (SSL) and 
    PyTorch regression models.
    """)
    st.info("This dashboard is the visualization layer for the 7-Step GeoAI Workflow proposed in Project SPROUT.")

with tab2:
    st.header("Generated Maps & Spatial Context")
    
    # Interactive PyDeck Map
    st.subheader("Interactive Study Area Map")
    st.write("Explore the Gamo Gofa region interactively (pan, zoom, and hover):")
    
    # Set the initial view state centered on Gamo Gofa, Ethiopia
    view_state = pdk.ViewState(
        latitude=6.0,
        longitude=37.0,
        zoom=7,
        pitch=0,
    )
    
    # Create a simple marker layer for the study area
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=[{"lat": 6.0, "lon": 37.0}],
        get_position=["lon", "lat"],
        get_radius=30000,
        get_color=[0, 255, 0, 160], # Green marker
        pickable=True,
    )
    
    # Render the map
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Gamo Gofa Study Area"},
    ))
    
    st.divider() # Adds a nice horizontal line
    
    # Original Static Publication Maps
    st.header("Publication-Ready Maps")
    st.write("These maps were generated using the custom Python scripts in the root directory.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Study Area")
        try:
            st.image("Publication_Study_Area_Map.png", caption="Gamo Gofa Study Area", width='stretch')
        except:
            st.warning("Study Area Map not found.")
            
    with col2:
        st.subheader("Land Cover Classification")
        try:
            st.image("Figure_4_Land_Cover_Maps.png", caption="Land Cover Maps", width='stretch')
        except:
            st.warning("Land Cover Map not found.")
            
    with col2:
        st.subheader("Land Cover Classification")
        try:
            st.image("Figure_4_Land_Cover_Maps.png", caption="Land Cover Maps", width='stretch')
        except:
            st.warning("Land Cover Map not found.")

with tab3:
    st.header("Model Pipeline & Architecture")
    st.markdown("""
    *   **Self-Supervised Learning (SSL):** `gamo_gofa_ssl_weights.pth` (Pre-trained backbone)
    *   **Carbon Regression Model:** `gamo_gofa_carbon_regression.pth` (Fine-tuned for biomass)
    *   **12-Band Inference:** `inference_12band.py` (Combines optical and SAR data)
    """)
    st.success("Models are currently stored locally and can be served via a FastAPI backend.")
