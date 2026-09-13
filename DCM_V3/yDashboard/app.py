import streamlit as st


st.set_page_config(
    page_title="LMU Women's Basketball Analytics",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("LMU Women's  Basketball Analytics")

st.markdown(
    """
    ## Basketball Analytics Dashboard

    This dashboard integrates team, player, DCM, lineup,
    combination, and progression analysis.
    """
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2: 

    st.image(
        "yDashboard/assets/FILM ROOM.png",
        use_container_width=False,
        
)
st.divider()

st.subheader("Dashboard")

st.markdown(
    """
    Use the navigation menu to explore:

    - **Overview** —  Team Overview
    - **Players DCM Ranking** — 
    - **Players Individual DCM** — 
    - **Aggregated Lineup Data** — 
    - **Individual Lineup Data** — 
    - **Combo Data** — 
    - **Progression** — longitudinal analysis
    """
)