import streamlit as st
import json
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import requests
from typing import Dict, Any, List
from shapely.geometry import Point, shape
import base64
from pathlib import Path
import os

# Get absolute path to this file's directory
CURRENT_DIR = Path(__file__).parent
LOGO_DIR = CURRENT_DIR / "logo"
DATA_DIR = CURRENT_DIR / "data"
STATES_DIR = CURRENT_DIR / "states"  # Directory for state data

# Set page configuration
st.set_page_config(
    page_title="India ASR Performance Analysis",
    layout="wide"
)

# Inject CSS for theme-aware styling
st.markdown("""
    <style>
    .sample-box {
        padding: 10px;
        background-color: var(--secondary-background-color);
        border-radius: 5px;
        color: var(--text-color);
        margin: 5px 0;
    }
    .metric-container {
        padding: 20px;
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        margin: 10px 0;
    }
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        padding: 1rem;
    }
    
    /* Audio Player Styles */
    .audio-container {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .audio-controls {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 10px;
    }
    
    .audio-player {
        width: 100%;
        height: 40px;
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .audio-player::-webkit-media-controls-panel {
        background-color: var(--secondary-background-color);
        border-radius: 20px;
    }
    
    .audio-player::-webkit-media-controls-play-button {
        background-color: var(--primary-color);
        border-radius: 50%;
        transform: scale(1.5);
    }
    
    .audio-player::-webkit-media-controls-current-time-display,
    .audio-player::-webkit-media-controls-time-remaining-display {
        color: var(--text-color);
        font-weight: bold;
    }
    
    .audio-player::-webkit-media-controls-volume-slider {
        background-color: var(--primary-color);
        border-radius: 25px;
        padding: 0 5px;
    }
    
    .download-button {
        display: inline-flex;
        align-items: center;
        padding: 5px 10px;
        background-color: var(--primary-color);
        color: white;
        border-radius: 5px;
        text-decoration: none;
        font-size: 14px;
        transition: background-color 0.3s;
    }
    
    .download-button:hover {
        background-color: var(--primary-color-dark);
    }
    
    .audio-info {
        font-size: 12px;
        color: var(--text-color);
        margin-top: 5px;
        opacity: 0.8;
    }
    
    /* Waveform visualization */
    .waveform {
        width: 100%;
        height: 60px;
        background: var(--secondary-background-color);
        position: relative;
        overflow: hidden;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    
    <script>
    function downloadAudio(url, filename) {
        fetch(url)
            .then(response => response.blob())
            .then(blob => {
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 0;
        margin-bottom: 20px;
    }
    
    .logo-img {
        max-height: 60px;
        width: auto;
    }
    
    .logo-title {
        color: var(--text-color);
        font-size: 24px;
        margin: 0;
        padding: 0;
    }
    </script>
""", unsafe_allow_html=True)

# Helper functions
def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        st.error(f"Error loading image {image_path}: {str(e)}")
        return ""
    
def add_logo():
    # Load all logos using absolute paths
    logo_artpark = LOGO_DIR / "ARTPARK.png"
    logo_iisc = LOGO_DIR / "IISC.png"
    logo_bhashini = LOGO_DIR / "bhashini.png"

    
    st.markdown(f"""
        <style>
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: var(--secondary-background-color);
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .navbar .title {{
            font-size: 50px;
            font-weight: bold;
            color: #00B4FF;
            font-family: Arial, sans-serif;
            text-decoration: none;
        }}
        .navbar .title:hover {{
            color: #0056b3;
            text-decoration: none;
        }}
        .navbar .subtitle {{
            font-size: 20px;
            color: var(--text-color);
            font-family: Arial, sans-serif;
            margin-top: -10px;
        }}
        .navbar .spacer {{
            flex-grow: 1;
        }}
        .navbar img {{
            max-height: 80px;
            width: auto;
        }}
        </style>
        
        <!-- Navbar -->
        <div class="navbar">
            <div>
                <a href="https://vaani.iisc.ac.in/" target="_blank" class="title">
                    VAANI
                </a>
                <div class="subtitle">State-of-the-art ASR performance on VAANI data</div>
            </div>
            <div class="spacer"></div>
            <img src="data:image/png;base64,{get_base64_encoded_image(logo_iisc)}" alt="IISC Logo">
            <img src="data:image/png;base64,{get_base64_encoded_image(logo_bhashini)}" alt="Bhashini Logo" style="max-height: 60px; width: auto; margin-right: 20px;">
            <a href="https://artpark.in/language-data-ai" target="_blank">
                <img src="data:image/png;base64,{get_base64_encoded_image(logo_artpark)}" alt="ARTPARK Logo">
            </a>
        </div>
    """, unsafe_allow_html=True)

    # Add spacing after navbar
    st.markdown("<br>", unsafe_allow_html=True)

def add_footer():
    logo_google = LOGO_DIR / "google.png"
    logo_bmgf = LOGO_DIR / "bmgf.png"
    logo_giz = LOGO_DIR / "giz-logo.png"
    st.markdown(f"""
        <style>
        .footer {{
            width: 100%;
            background-color: white;
            text-align: center;
            padding: 120px 0;
            margin-top: 100px;
            border-top: 1px solid #eee;
        }}
        .footer-content {{
            display: flex;
            justify-content: center;
            align-items: center;
            max-width: 800px;
            margin: 0 auto;
        }}
        .footer img.google-logo {{
            height: 100px;
            width: auto;
            object-fit: contain;
        }}
        .footer img.bhashini-logo {{
            height: 350px;  /* Increased height for Bhashini logo */
            width: auto;
            object-fit: contain;
            margin-left: -10px;  /* Negative margin to bring logos closer */
        }}
        .footer img {{
            height: 80px;
            width: auto;
            object-fit: contain;
            margin: 0 20px;
        }}
        
        .footer-text {{
            color: #666;
            font-size: 14px;
            margin-bottom: -50px;  /* Decreased bottom margin */
            margin-top: 0px;    /* Decreased top margin */
        }}
        </style>
        
        <div class="footer">
            <div class="footer-text">Supported By</div>
            <div class="footer-content">
                <img class="bhashini-logo" src="data:image/png;base64,{base64.b64encode(open(logo_google, 'rb').read()).decode()}" alt="Google Logo">
                <img src="data:image/png;base64,{base64.b64encode(open(logo_bmgf, 'rb').read()).decode()}" alt="BMGF Logo">
                <img src="data:image/png;base64,{base64.b64encode(open(logo_giz, 'rb').read()).decode()}" alt="GIZ Logo">
            </div>
        </div>
    """, unsafe_allow_html=True)
    
def load_state_geojson(state_name: str) -> Dict[str, Any]:
    """Load GeoJSON for specified state"""
    file_path = STATES_DIR / f"{state_name}.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {state_name} GeoJSON: {str(e)}")
        return None

def load_data():
    """Load sample data for ASR metrics"""
    try:
        file_path = DATA_DIR / "sample5renamed.json.json" # Using updated filename from your paste
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def get_color(wer):
    wer = float(wer)
    if wer <= 20:
        return '#00ff00'  # bright green
    elif wer <= 50:
        return '#ffa500'  # orange
    else:
        return '#ff0000'  # red

def find_clicked_district(clicked_lat, clicked_lng, all_geojsons, model_data):
    """Find which district was clicked on the map across all states"""
    click_point = Point(clicked_lng, clicked_lat)
    
    for state_name, geojson_data in all_geojsons.items():
        if not geojson_data:
            continue
            
        for feature in geojson_data['features']:
            district = feature['properties']['district']
            if district in model_data:
                try:
                    if shape(feature['geometry']).contains(click_point):
                        return state_name, district
                except Exception:
                    continue
    
    return None, None

def add_wer_to_geojson(geojson_data, model_data):
    """Add WER data from model to GeoJSON properties"""
    for feature in geojson_data['features']:
        district = feature['properties']['district']
        district = district.strip().title()  # Normalize format
        if district in model_data:
            feature['properties']['wer'] = f"{model_data[district]['WER']}%"
        else:
            # Debug print for missing districts
            feature['properties']['wer'] = 'N/A'
    return geojson_data

def main():
    # Initialize session state
    if 'clicked_district' not in st.session_state:
        st.session_state['clicked_district'] = None
    if 'clicked_state' not in st.session_state:
        st.session_state['clicked_state'] = None
    if 'last_click' not in st.session_state:
        st.session_state['last_click'] = None
    
    # Load available states
    available_states = [f.stem for f in STATES_DIR.glob("*.json") if f.is_file()]
    
    add_logo()
    
    # Main heading
    st.markdown("<h2 style='color: #203454;'>Speech Recognition Performance Analysis - All India</h2>", unsafe_allow_html=True)
    
    # Explanation
    st.markdown("<p style='color: #203454;'>Automatic speech recognition performance is computed using <a href='https://en.wikipedia.org/wiki/Word_error_rate' target='_blank' style='color: #00B4FF;'>Word Error Rate (WER)</a>.</p>", unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    if data is None:
        st.error("Failed to load data")
        return
    
    # Create two columns for map and analysis
    map_col, analysis_col = st.columns([4, 2])
    
    with analysis_col:
        st.subheader("Data Summary")
        st.write(f"Models: {len(data)}")
        st.write(f"Districts: {len(data['AWS'])}")
        st.write(f"States: 12 ")
        
        model_options = list(data.keys())
        selected_model = st.selectbox(
            "Select Model",
            options=model_options,
            index=len(model_options) - 1
        )
        
        # District selector dropdown (similar to previous version, no state dropdown)
        if st.session_state['clicked_district']:
            default_ix = list(data[selected_model].keys()).index(st.session_state['clicked_district'])
        else:
            default_ix = 0
            
        selected_district_sidebar = st.selectbox(
            "Select District",
            options=list(data[selected_model].keys()),
            index=default_ix,
            key='district_selector'
        )
        
        if st.session_state.get('district_selector') != st.session_state['clicked_district']:
            st.session_state['clicked_district'] = selected_district_sidebar
        
        # Display district analysis if selected
        if st.session_state['clicked_district'] and st.session_state['clicked_district'] in data[selected_model]:
            district_data = data[selected_model][st.session_state['clicked_district']]
            
            st.markdown(
                f"""
                <div class="metric-container" style="text-align: center;">
                    <h4>{st.session_state['clicked_district']} Word Error Rate (WER)</h4>
                    <h2 style="color: {get_color(district_data['WER'])}">{district_data['WER']}%</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Show state if available
            if st.session_state['clicked_state']:
                st.write(f"State: {st.session_state['clicked_state']}")
    
    with map_col:
        # WER Thresholds legend
        st.markdown("""
            <div style="position: absolute; top: 20px; left: 35px; padding: 20px; background-color: var(--secondary-background-color); border-radius: 10px; display: flex; justify-content: space-around; z-index: 1000;">
                <div style="display: flex; align-items: center; margin-right: 10px;">
                    <div style="width: 20px; height: 20px; background-color: #00ff00; margin-right: 10px; opacity: 0.7; border: 1px solid var(--text-color);"></div>
                    <span style="color: var(--text-color);">WER ≤ 20%</span>
                </div>
                <div style="display: flex; align-items: center; margin-right: 10px;">
                    <div style="width: 20px; height: 20px; background-color: #ffa500; margin-right: 10px; opacity: 0.7; border: 1px solid var(--text-color);"></div>
                    <span style="color: var(--text-color);">20% < WER ≤ 50%</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 20px; height: 20px; background-color: #ff0000; margin-right: 10px; opacity: 0.7; border: 1px solid var(--text-color);"></div>
                    <span style="color: var(--text-color);">WER > 50%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Load all state GeoJSONs
        all_geojsons = {}
        for state in available_states:
            geojson = load_state_geojson(state)
            if geojson:
                # Add WER data to GeoJSON
                geojson = add_wer_to_geojson(geojson, data[selected_model])
                all_geojsons[state] = geojson
        
        # India map bounds
        INDIA_BOUNDS = [[8.0, 68.0], [37.0, 97.0]]
        
        # Create map
        m = folium.Map(
            location=[23.0, 82.0],  # Center of India (approx)
            zoom_start=5,  # Increased zoom level by 1
            tiles='OpenStreetMap',
            min_zoom=5,
            max_zoom=10,
            scrollWheelZoom=True,  # Enable scrolling for the all-India view
            dragging=True  # Enable dragging for the all-India view
        )
        
        # Add all states to the map
        for state_name, geojson_data in all_geojsons.items():
            if not geojson_data:
                continue
                
            # Define style function for this layer
            def style_function(feature, state_name=state_name):
                district_name = feature['properties']['district']
                # Check if this is the clicked district
                is_clicked = (district_name == st.session_state['clicked_district'] and 
                             state_name == st.session_state['clicked_state'])
                
                if district_name in data[selected_model]:
                    return {
                        'fillColor': '#ff000066' if is_clicked else get_color(data[selected_model][district_name]['WER']),
                        'color': 'black',
                        'weight': 3 if is_clicked else 1,
                        'fillOpacity': 0.9 if is_clicked else 0.7,
                        'dashArray': '5, 5' if is_clicked else None
                    }
                return {
                    'fillColor': '#CCCCCC',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.4
                }
            
            # Add this state's districts to the map
            folium.GeoJson(
                geojson_data,
                name=state_name,
                style_function=lambda x, state=state_name: style_function(x, state),
                highlight_function=lambda x: {
                    'fillColor': '#ff000066',
                    'weight': 3,
                    'fillOpacity': 0.9
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=['district', 'wer'],
                    aliases=['District:', 'WER:'],
                    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                )
            ).add_to(m)
        
        # Fit the map to India bounds
        m.fit_bounds(INDIA_BOUNDS)
        
        # Show the map
        map_data = st_folium(m, width=1120, height=700, key="map")
        
        # Handle clicking on the map
        if (map_data is not None and 'last_clicked' in map_data and 
            map_data['last_clicked'] and map_data['last_clicked'] != st.session_state['last_click']):
            
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']
            
            clicked_state, clicked_district = find_clicked_district(
                clicked_lat, 
                clicked_lng, 
                all_geojsons, 
                data[selected_model]
            )
            
            if clicked_district:
                st.session_state['clicked_state'] = clicked_state
                st.session_state['clicked_district'] = clicked_district
                st.session_state['last_click'] = map_data['last_clicked']
                st.rerun()
    
    # Sample Analysis section
    st.markdown("### Sample Analysis")
    if st.session_state['clicked_district'] and st.session_state['clicked_district'] in data[selected_model]:
        district_data = data[selected_model][st.session_state['clicked_district']]
        
        # Display state information if available
        if st.session_state['clicked_state']:
            st.markdown(f"**State:** {st.session_state['clicked_state']}")
        
        # Create columns for samples
        left_col, right_col = st.columns(2)
        
        samples = list(district_data['Samples'].items())
        mid_point = (len(samples) + 1) // 2
        
        # Left column samples
        with left_col:
            for sample_id, sample_data in samples[:mid_point]:
                with st.expander(f"{sample_id}", expanded=True):
                    audio_col, download_col = st.columns([3, 1])
                    with audio_col:
                        st.audio(sample_data['URL'], format='audio/wav')
                    with download_col:
                        st.markdown(f"""
                            <div style="height: 40px; display: flex; align-items: center; justify-content: center;">
                                <a href="{sample_data['URL']}" 
                                   style="text-decoration: none; padding: 8px 15px; background-color: var(--primary-color); 
                                          color: white; border-radius: 5px; display: inline-flex; align-items: center; gap: 5px;"
                                   download="sample_{sample_id}.wav" target="_blank">
                                    <span>📥</span> Download
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("**Model Output:**")
                    st.markdown(f"""<div class="sample-box">{sample_data['ModelOutput']}</div>""", unsafe_allow_html=True)
                    st.markdown("**Reference:**")
                    st.markdown(f"""<div class="sample-box">{sample_data['Reference']}</div>""", unsafe_allow_html=True)
        
        # Right column samples
        with right_col:
            for sample_id, sample_data in samples[mid_point:]:
                with st.expander(f"{sample_id}", expanded=True):
                    audio_col, download_col = st.columns([3, 1])
                    with audio_col:
                        st.audio(sample_data['URL'], format='audio/wav')
                    with download_col:
                        st.markdown(f"""
                            <div style="height: 40px; display: flex; align-items: center; justify-content: center;">
                                <a href="{sample_data['URL']}" 
                                   style="text-decoration: none; padding: 8px 15px; background-color: var(--primary-color); 
                                          color: white; border-radius: 5px; display: inline-flex; align-items: center; gap: 5px;"
                                   download="sample_{sample_id}.wav" target="_blank">
                                    <span>📥</span> Download
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("**Model Output:**")
                    st.markdown(f"""<div class="sample-box">{sample_data['ModelOutput']}</div>""", unsafe_allow_html=True)
                    st.markdown("**Reference:**")
                    st.markdown(f"""<div class="sample-box">{sample_data['Reference']}</div>""", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    add_footer()

if __name__ == "__main__":
    main()