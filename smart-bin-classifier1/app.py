import streamlit as st
import pandas as pd
from PIL import Image
import os
from src.search_engine import BinSearchSystem

st.set_page_config(page_title="Smart Bin Classifier", layout="wide")

IMG_DIR = "data/bin-images"
META_DIR = "data/metadata"

# --- Initialize System (Cached) ---
@st.cache_resource
def load_system():
    # check if data exists
    if not os.path.exists(IMG_DIR) or len(os.listdir(IMG_DIR)) == 0:
        return None
    
    system = BinSearchSystem(IMG_DIR, META_DIR)
    system.build_index()
    return system

st.title("📦 Smart Bin Inventory Check")
st.markdown("Upload an image of a bin to identify its contents based on the Amazon Bin Dataset.")

system = load_system()

if system is None:
    st.error("⚠️ Data not found! Please run `python src/download_data.py` first.")
else:
    # --- Sidebar ---
    with st.sidebar:
        st.header("Upload Bin Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    # --- Main Interface ---
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        # 1. Display Upload
        image = Image.open(uploaded_file)
        with col1:
            st.info("Your Upload")
            st.image(image, use_container_width=True)

        # 2. Perform Search
        with st.spinner('Analyzing visual features...'):
            match_fname, score, metadata = system.search(image)
        
        # 3. Display Match
        match_path = os.path.join(IMG_DIR, match_fname)
        with col2:
            st.success(f"Best Match Found (Diff: {score:.2f})")
            st.image(Image.open(match_path), use_container_width=True)
            st.caption(f"Matched File: {match_fname}")

        # 4. Display Inventory Data
        st.divider()
        st.subheader("📋 Verified Inventory (Metadata)")
        
        if "BIN_FCSKU_DATA" in metadata:
            items = metadata["BIN_FCSKU_DATA"]
            # Convert JSON to nice Table
            df = pd.DataFrame.from_dict(items, orient='index')
            st.dataframe(df[["name", "quantity", "asin", "weight"]], use_container_width=True)
        else:
            st.write(metadata)
