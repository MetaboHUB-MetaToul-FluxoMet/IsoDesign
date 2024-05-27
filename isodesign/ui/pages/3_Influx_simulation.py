import streamlit as st
from sess_i.base.main import SessI

session = SessI(
        session_state=st.session_state,
        page="3_influx_simulation")

st.set_page_config(page_title="IsoDesign 2.0")
st.title("Influx simulation")

st.header("Run parameters")
# st.write(session)

# st.checkbox("Feasibility domain projection", value=True)