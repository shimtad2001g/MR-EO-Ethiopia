import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Project SPROUT: MR-EO Ethiopia", layout="wide")

# Force custom SPROUT theme via CSS
st.markdown("""
    <style>
    /* Tabs */
    .stTabs [data-baseweb="tab-highlight"] { background-color: #2E7D32 !important; }
    .stTabs [data-baseweb="tab"] { color: #2E7D32 !important; }
    .stTabs [aria-selected="true"] { color: #2E7D32 !important; font-weight: bold !important; }
    /* Alerts */
    div[data-testid="stAlert"] { background-color: #E8F5E9 !important; border: 1px solid #2E7D32 !important; }
    div[data-testid="stAlert"] * { color: #1B5E20 !important; }
    /* Background */
    .stApp { background-color: #F8F9FA !important; }
    </style>
""", unsafe_allow_html=True)

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
    st.write("Explore the 5 validation zones in the Gamo Gofa region (pan, zoom, and hover over markers):")
    
    # Create a DataFrame with the 5 validation zones
    map_data = pd.DataFrame({
        "Zone": ["Z1: Wurch (Afro-alpine)", "Z2: Dega (Highland)", "Z3: Weyna Dega (Mid-alt)", "Z4: Kolla (Lowland)", "Z5: Bereha (Arid)"],
        "lat": [6.8, 6.2, 6.0, 6.9, 5.6],
        "lon": [36.8, 36.6, 37.0, 37.4, 37.6],
        "color": [
            [128, 0, 128, 160],  # Purple
            [0, 255, 0, 160],    # Green
            [255, 255, 0, 160],  # Yellow
            [255, 165, 0, 160],  # Orange
            [255, 0, 0, 160]     # Red
        ]
    })
    
    # Set the initial view state
    view_state = pdk.ViewState(
        latitude=6.2,
        longitude=37.1,
        zoom=7,
        pitch=0,
    )
    
    # Create the marker layer using the DataFrame
    layer = pdk.Layer(
        "ScatterplotLayer",
        map_data,
        get_position=["lon", "lat"],
        get_radius=20000,
        get_fill_color="color",
        pickable=True,
    )
    
    # Render the map
    st.pydeck_chart(
        pdk.Deck(
            map_style="carto-positron", 
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"text": "{Zone}"},
        ), 
        use_container_width=True,
        key="interactive_map_zones" 
    )
    
    st.divider()
    
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

with tab3:
    st.header("Model Pipeline & Architecture")
    st.write("This project utilizes a 7-Step GeoAI workflow, combining Self-Supervised Learning (SSL) with PyTorch regression models.")
    
    # Add the framework flowchart
    try:
        st.image("Figure_2_Framework_Flowchart.png", caption="Project SPROUT GeoAI Framework Flowchart", width='stretch')
    except:
        st.warning("Framework flowchart not found in the repository.")
        
    st.divider()
    
    # Two columns for detailed model info
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 Deep Learning Models")
        st.markdown("""
        *   **Self-Supervised Learning (SSL):** `gamo_gofa_ssl_weights.pth` 
            *(Pre-trained backbone for feature extraction)*
        *   **Carbon Regression Model:** `gamo_gofa_carbon_regression.pth` 
            *(Fine-tuned for above-ground biomass estimation)*
        """)
        
    with col2:
        st.subheader("⚙️ Inference & Deployment")
        st.markdown("""
        *   **12-Band Inference:** `inference_12band.py` 
            *(Combines optical and SAR data)*
        *   **Backend API:** Models can be served via a FastAPI backend for real-time predictions.
        """)
        
    st.success("Models are currently stored locally and can be integrated into the FastAPI backend.")