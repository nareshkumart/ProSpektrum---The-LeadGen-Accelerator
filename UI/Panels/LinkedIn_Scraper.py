# Importing Required Modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
import streamlit as st
import sys
sys.path.append('..')
from Bots.lead_gen_bot import lead_gen_accelerator
import os
from io import BytesIO

def create_excel_bytes(df_list, sheet_name_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for i in range(len(df_list)):
            df_list[i].to_excel(writer, sheet_name=sheet_name_list[i], index=False)
    output.seek(0)
    return output

def linkedin_scraper_panel():
    st.title("LinkedIn Scraper")
    company_name = st.text_input("Account Name")
    geography = st.text_input("Geography")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        pass
    with col2:
        pass
    with col3:
        st.write(" ")
        next_button = st.button("Proceed")
    with col4:
        pass
    with col5:
        pass

    if geography:
        linkedin_username = st.text_input("LinkedIn Username")
        linkedin_password = st.text_input("LinkedIn Password", type="password")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            pass
        with col2:
            pass
        with col3:
            st.write(" ")
            scrape_button = st.button('   Start Scraping   ')
        with col4:
            pass
        with col5:
            pass

        if scrape_button:
            try:
                excel_data = lead_gen_accelerator(linkedin_username, linkedin_password, company_name, geography)
            except Exception as e:
                print(f"Error {e} occured")
            with col1:
                pass
            with col2:
                pass
            with col3:
                if excel_data is not None:
                    st.write(" ")
                    st.download_button(label='Download Excel File', data= excel_data, file_name=f"{company_name}_exported_leads.xlsx", key='download_button')
            with col4:
                pass
            with col5:
                pass