import streamlit as st
from Panels.Introduction import introduction_panel
from Panels.Apollo_Scraper import apollo_scraper_panel
from Panels.LinkedIn_Scraper import linkedin_scraper_panel
from Panels.Contact_us import contact_us_panel
from PIL import Image
import os

col1,col2,col3,col4,col5 = st.columns(5)
with col1:
    pass
with col2:
    logo_path = os.path.join(os.path.dirname(os.getcwd()),'Logo','prospektrum_logo.png')
    logo = Image.open(logo_path)
    st.image(logo,width = 352)
with col3:
    pass
with col4:
    pass
with col5:
    pass

tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "LinkedIn Scraper", "Apollo Scraper", "Contact Us"])

with tab1:
    introduction_panel()
with tab2:
    linkedin_scraper_panel()
with tab3:
    apollo_scraper_panel()
with tab4:
    contact_us_panel()