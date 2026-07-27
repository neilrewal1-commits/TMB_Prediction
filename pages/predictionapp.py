import pickle

import pandas as pd
import streamlit as st

# Require user authentication
if not st.user.is_logged_in:
    st.error("Please log in to access the app.")
    st.stop()

@st.cache_resource
def load_model(model_path):
    """Load and cache the trained classification model."""
    with open(model_path, "rb") as model_file:
        model = pickle.load(model_file)

    return model

MODEL_PATH = 'Best_Model_RF_50Trees_7Depth (1)'
