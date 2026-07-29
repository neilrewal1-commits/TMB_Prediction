import streamlit as st
imageaddress = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSAb7MGqnR-lSnIMuqLaO_sM1n1GMRWosIvbx_HmWfewg&s=10'
st.title('Predicting Stomach Adenocarcinoma TMB Status')

st.image(
    image_address,
    caption="Stomach Adenocarcinoma TMB Classification",
)

if not st.user.is_logged_in:
    if st.sidebar.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()

else:
  if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
        st.logout()
        st.stop()
