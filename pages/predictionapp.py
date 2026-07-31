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




MODEL_PATH = "stomach_adenocarcinoma_tmb_best_lr_model_updated"

LABELS = {
    0: "Low TMB",
    1: "High TMB",
}



st.title("Stomach Adenocarcinoma TMB Classification")

st.subheader("Upload Gene Mutation Features")

uploaded_file = st.file_uploader(
    "Upload a CSV file containing the gene features",
    type=["csv"],
    accept_multiple_files=False,
)

if uploaded_file is None:
    st.info("Upload a CSV file to get started.")
else:    

    try:
        dataframe = pd.read_csv(uploaded_file)

    except (
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as error:
        st.error(f"The file could not be read as a CSV: {error}")
        

    if dataframe.empty:
        st.error("The uploaded CSV file does not contain any data.")
        

    st.subheader("Data Preview")
    st.dataframe(
        dataframe,
        use_container_width=True,
        hide_index=True,
    )

    try:
        with st.spinner("Processing..."):
            classification_model = load_model(MODEL_PATH)

            predictions = classification_model.predict(dataframe)

            result_dataframe = dataframe.copy()
            result_dataframe["Prediction"] = [
                LABELS.get(int(prediction), "Unknown")
                for prediction in predictions
            ]

        if len(predictions) == 1:
            prediction = int(predictions[0])
            st.success(f"Prediction: {LABELS.get(prediction, 'Unknown')}")

        else:
            st.success(
                f"Successfully classified {len(predictions)} samples."
            )

            st.subheader("Classification Results")
            st.dataframe(
                result_dataframe,
                use_container_width=True,
                hide_index=True,
            )

    except FileNotFoundError:
        st.error(f"Model file not found: {MODEL_PATH}")

    except ValueError as error:
        st.error(
            "The uploaded data does not match the features expected by "
            f"the model. Details: {error}"
        )

    except Exception as error:
        st.error(f"An unexpected error occurred: {error}")


