import streamlit as st
import json
import folium
from streamlit_folium import folium_static, st_folium
import pandas as pd
import requests
from typing import Dict, Any

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
    .legend {
        color: black;
        background-color: white;
    }
    /* Make the sidebar visible */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

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
        return '#ff0000'  # bright red

def find_clicked_district(clicked_lat, clicked_lng, geojson_data, model_data):
    """Find the district that was clicked on the map"""
    from shapely.geometry import Point, shape
    
    click_point = Point(clicked_lng, clicked_lat)
    
    for feature in geojson_data['features']:
        district = feature['properties']['district']
        if district in model_data:
            if shape(feature['geometry']).contains(click_point):
                return district
    return None

def main():
    st.title("Model WER Analysis on Karnataka Map")
    
    # Initialize session state
    if 'clicked_district' not in st.session_state:
        st.session_state.clicked_district = None
    if 'last_click' not in st.session_state:
        st.session_state.last_click = None
    
    # Sidebar setup
    with st.sidebar:
        st.title("Settings")
        
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

    # Create map
    m = folium.Map(location=[15.3173, 75.7139], zoom_start=7)
    
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

    # Add GeoJSON layer
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
    
    # Add legend
    legend_html = '''
    <div class="legend" style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <p><strong>WER Ranges</strong></p>
        <p><span style="color: #00ff00;">■</span> 0-20%</p>
        <p><span style="color: #ffa500;">■</span> 20-50%</p>
        <p><span style="color: #ff0000;">■</span> >50%</p>
        <p><span style="color: #CCCCCC;">■</span> No Data</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Display map and handle clicks
    map_data = st_folium(m, width=1200, height=600, key="map")
    
    # Update clicked district based on map interaction
    if map_data['last_clicked'] and map_data['last_clicked'] != st.session_state.last_click:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        st.session_state.clicked_district = find_clicked_district(
            clicked_lat, 
            clicked_lng, 
            karnataka_geojson, 
            data[selected_model]
        )
        st.session_state.last_click = map_data['last_clicked']
        st.experimental_rerun()
    
    # Display samples for clicked district
    if st.session_state.clicked_district and st.session_state.clicked_district in data[selected_model]:
        district_data = data[selected_model][st.session_state.clicked_district]
        
        # Display district header and WER
        st.markdown(f"### {st.session_state.clicked_district} District Analysis")
        st.markdown(
            f"""
            <div class="metric-container" style="text-align: center;">
                <h4>Word Error Rate (WER)</h4>
                <h2 style="color: {get_color(district_data['WER'])}">{district_data['WER']}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display samples in a cleaner format
        st.markdown("### Samples")
        for sample_id, sample_data in district_data['Samples'].items():
            with st.expander(f"Sample {sample_id}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Model Output:**")
                    st.markdown(
                        f"""<div class="sample-box">{sample_data['Model_Output']}</div>""",
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown("**Reference:**")
                    st.markdown(
                        f"""<div class="sample-box">{sample_data['Reference']}</div>""",
                        unsafe_allow_html=True
                    )

if __name__ == "__main__":
    main()