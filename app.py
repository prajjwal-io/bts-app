import streamlit as st
import json
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import requests
from typing import Dict, Any
from shapely.geometry import Point, shape

# Set page configuration
st.set_page_config(
    page_title="Model WER Analysis",
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

def add_logo():
    col1, col2 = st.columns([0.5, 4])
    with col1:
        st.image("ARTPARK.png", width=160)

def load_karnataka_geojson() -> Dict[str, Any]:
    url = "https://raw.githubusercontent.com/adarshbiradar/maps-geojson/master/states/karnataka.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error loading Karnataka GeoJSON: {str(e)}")
        return None

def load_data(file_path=None):
    if file_path is None:
        st.error("Please provide a valid JSON file path in the sidebar")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid JSON file format")
        return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def get_color(wer):
    wer = float(wer)
    if wer <= 20:
        return '#00ff00'  # bright green
    elif wer <= 50:
        return '#ffa500'  # orange
    else:
        return '#ff0000'  # red

def find_clicked_district(clicked_lat, clicked_lng, geojson_data, model_data):
    click_point = Point(clicked_lng, clicked_lat)
    for feature in geojson_data['features']:
        district = feature['properties']['district']
        if district in model_data:
            try:
                if shape(feature['geometry']).contains(click_point):
                    return district
            except:
                continue
    return None

def main():
    st.title("Model WER Analysis Dashboard")
    
    # Initialize session state
    if 'clicked_district' not in st.session_state:
        st.session_state.clicked_district = None
    if 'last_click' not in st.session_state:
        st.session_state.last_click = None
    
    # Sidebar setup
    with st.sidebar:
        add_logo()        
        file_path = st.text_input(
            "Enter JSON file path",
            value="",
            help="Enter the full path to your JSON file"
        )
        
        uploaded_file = st.file_uploader(
            "Or upload a JSON file",
            type=['json'],
            help="Upload your JSON file directly"
        )
        
        data = None
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
            except Exception as e:
                st.error(f"Error loading uploaded file: {str(e)}")
        elif file_path:
            data = load_data(file_path)
        
        if data is None:
            st.info("Please provide a JSON file to visualize the data")
            return
        
        selected_model = st.selectbox(
            "Select Model",
            options=list(data.keys())
        )
        
        st.subheader("Data Summary")
        st.write(f"Number of models: {len(data)}")
        st.write(f"Districts in selected model: {len(data[selected_model])}")
        
        # Add district dropdown without disrupting click behavior
        if st.session_state.clicked_district:
            default_ix = list(data[selected_model].keys()).index(st.session_state.clicked_district)
        else:
            default_ix = 0
            
        selected_district_sidebar = st.selectbox(
            "Select District",
            options=list(data[selected_model].keys()),
            index=default_ix,
            key='district_selector'
        )
        
        # Only update if explicitly changed through dropdown
        if st.session_state.get('district_selector') != st.session_state.clicked_district:
            st.session_state.clicked_district = selected_district_sidebar
    
    # Load Karnataka GeoJSON
    karnataka_geojson = load_karnataka_geojson()
    if karnataka_geojson is None:
        st.error("Failed to load Karnataka district boundaries")
        return

    # Create two columns - one for map and one for thresholds
    map_col, threshold_col = st.columns([4, 1])  # 4:1 ratio
    
    with map_col:
        # Define Karnataka bounds
        KARNATAKA_BOUNDS = [
            [11.5, 74.0],  # Southwest corner
            [18.5, 78.5]   # Northeast corner
        ]
        # Create map
        m = folium.Map(
            location=[15.3173, 75.7139],  # Center of Karnataka
            zoom_start=7,
            tiles='OpenStreetMap',
            min_zoom=7,  # Restrict minimum zoom
            max_zoom=10,  # Restrict maximum zoom
            min_lat=KARNATAKA_BOUNDS[0][0],  # Restrict panning
            max_lat=KARNATAKA_BOUNDS[1][0],
            min_lon=KARNATAKA_BOUNDS[0][1],
            max_lon=KARNATAKA_BOUNDS[1][1],
        )
        
        #Style function for districts
        def style_function(feature):
            district_name = feature['properties']['district']
            if district_name in data[selected_model]:
                return {
                    'fillColor': get_color(data[selected_model][district_name]['WER']),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7
                }
            return {
                'fillColor': '#CCCCCC',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.4
            }
        
        mask = folium.FeatureGroup(name='mask')

            # Add white mask around Karnataka
        mask_coordinates = [
            [[90, 0], [90, 90], [0, 90], [0, 0]],  # World bounds
            karnataka_geojson['features'][0]['geometry']['coordinates'][0]  # Karnataka boundary
        ]
        
        folium.Polygon(
            locations=mask_coordinates,
            color='white',
            fill=True,
            fill_color='white',
            fill_opacity=0.8,
        ).add_to(mask)
        
        # Add the mask to the map
        mask.add_to(m)


        # Add districts layer
        districts = folium.GeoJson(
            karnataka_geojson,
            style_function=style_function,
            highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.9},
            tooltip=folium.GeoJsonTooltip(
                fields=['district'],
                aliases=['District:'],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        ).add_to(m)

        # Fit the map to Karnataka bounds
        m.fit_bounds(KARNATAKA_BOUNDS)

        
        # Display map
        map_data = st_folium(m, width=1000, height=700, key="map")
    
    with threshold_col:

        st.markdown("""
            <div style="
                padding: 15px;
                background-color: var(--secondary-background-color);
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-top: 20px;
                color: var(--text-color);
            ">
                <h4 style="text-align: center; margin-bottom: 15px; color: var(--text-color);">WER Thresholds</h4>
                <div style="margin: 10px 0;">
                    <div style="
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        background-color: #00ff00;
                        margin-right: 10px;
                        vertical-align: middle;
                        opacity: 0.7;
                        border: 1px solid var(--text-color);
                    "></div>
                    <span style="color: var(--text-color);">WER ≤ 20%</span>
                </div>
                <div style="margin: 10px 0;">
                    <div style="
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        background-color: #ffa500;
                        margin-right: 10px;
                        vertical-align: middle;
                        opacity: 0.7;
                        border: 1px solid var(--text-color);
                    "></div>
                    <span style="color: var(--text-color);">20% < WER ≤ 50%</span>
                </div>
                <div style="margin: 10px 0;">
                    <div style="
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        background-color: #ff0000;
                        margin-right: 10px;
                        vertical-align: middle;
                        opacity: 0.7;
                        border: 1px solid var(--text-color);
                    "></div>
                    <span style="color: var(--text-color);">WER > 50%</span>
                </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Update clicked district based on map interaction
    if map_data['last_clicked'] and map_data['last_clicked'] != st.session_state.last_click:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        clicked_district = find_clicked_district(
            clicked_lat, 
            clicked_lng, 
            karnataka_geojson, 
            data[selected_model]
        )
        if clicked_district:
            st.session_state.clicked_district = clicked_district
            st.session_state.last_click = map_data['last_clicked']
            st.experimental_rerun()
    
    # Display analysis for selected district
    if st.session_state.clicked_district and st.session_state.clicked_district in data[selected_model]:
        district_data = data[selected_model][st.session_state.clicked_district]
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f"""
                <div class="metric-container" style="text-align: center;">
                    <h3>{st.session_state.clicked_district} District Analysis</h3>
                    <h4>Word Error Rate (WER)</h4>
                    <h2 style="color: {get_color(district_data['WER'])}">{district_data['WER']}%</h2>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Display samples
        # Display samples
    st.markdown("### Sample Analysis")
    for sample_id, sample_data in district_data['Samples'].items():
        with st.expander(f"Sample {sample_id}", expanded=True):
            # Add audio player using st.audio
            st.subheader(f"Audio Sample {sample_id}")
            
            # Audio player with download button in a row
            col1, col2 = st.columns([3, 1])
            with col1:
                st.audio(sample_data['URL'], format='audio/wav')
            with col2:
                st.markdown(f"""
                    <div style="height: 40px; display: flex; align-items: center; justify-content: center;">
                        <a href="{sample_data['URL']}" 
                        style="text-decoration: none; 
                                padding: 8px 15px; 
                                background-color: var(--primary-color); 
                                color: white; 
                                border-radius: 5px;
                                display: inline-flex;
                                align-items: center;
                                gap: 5px;"
                        download="sample_{sample_id}.wav" 
                        target="_blank">
                            <span>📥</span> Download
                        </a>
                    </div>
                """, unsafe_allow_html=True)
            
            # Format info
            st.markdown("""
                <div style="font-size: 12px; color: var(--text-color); opacity: 0.8; margin-top: 5px;">
                    Format: WAV | Use player controls or download for offline listening
                </div>
            """, unsafe_allow_html=True)

            # Model output and reference
            transcription_cols = st.columns(2)
            
            with transcription_cols[0]:
                st.markdown("**Model Output:**")
                st.markdown(
                    f"""<div class="sample-box">{sample_data['Model_Output']}</div>""",
                    unsafe_allow_html=True
                )
            
            with transcription_cols[1]:
                st.markdown("**Reference:**")
                st.markdown(
                    f"""<div class="sample-box">{sample_data['Reference']}</div>""",
                    unsafe_allow_html=True
                )
            
            # Add keyboard shortcuts info
            st.markdown("""
                <div style="font-size: 12px; color: var(--text-color); margin-top: 10px; opacity: 0.8;">
                    Keyboard shortcuts: Space - Play/Pause | → - Forward | ← - Backward | ↑ - Volume Up | ↓ - Volume Down
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()