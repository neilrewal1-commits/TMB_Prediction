import streamlit as st

IMAGE_ADDRESS = ("https://scmsc.com/wp-content/uploads/2024/12/3D-illustration-of-stomach-cancer.jpg")

# Home page
st.title("Stomach Adenocarcinoma TMB Classification")

# Add a coral reef image
st.image(
    IMAGE_ADDRESS,
    caption="Stomach Adenocarcinoma TMB Classification",
)


if not st.user.is_logged_in:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
        st.stop()
