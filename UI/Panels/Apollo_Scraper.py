import pandas as pd
import streamlit as st
import sys
import time
from datetime import datetime
import random
sys.path.append('..')
from tqdm import tqdm
from Bots.apollo_scraper_bot import apollo_driver_setup, fetch_mail_from_apollo

def apollo_scraper_panel():
    st.title("Apollo Scraper")

    file = st.file_uploader("Upload a file", type=["xlsx"])
    if file:
        xls = pd.ExcelFile(file)
        sheet_names = xls.sheet_names
        co1, co2, co3, co4, co5 = st.columns(5)

        with co1:
            pass
        with co2:
            pass
        with co3:
            st.write(" ")
            selected_sheet = st.selectbox("Select Sheet", sheet_names)
        with co4:
            pass
        with co5:
            pass
        
        if selected_sheet is not None:

            df = pd.read_excel(xls, sheet_name=selected_sheet)
            st.table(df.head(5))
            apollo_username = st.text_input("Apollo Username")
            apollo_password = st.text_input("Apollo Password", type="password")
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                pass
            with col2:
                pass
            with col3:
                st.write(" ")
                scrape_button = st.button("   Fetch Mail IDs   ")
            with col4:
                pass
            with col5:
                pass

            if scrape_button:
                apollo_driver = apollo_driver_setup(apollo_username,apollo_password)
                time.sleep(random.uniform(2,3))
                mail_id_list = []

                # Fetching correct Mail IDs from Apollo
                for i in tqdm(range(len(df)), desc = 'Scraping mails'):
                    mail_id = fetch_mail_from_apollo(apollo_driver,f"{df['Employee_name'][i]} {df['Current_company'][i]}")
                    if i>0:
                        if mail_id in mail_id_list:
                            mail_id_list.append("Not found in Apollo")
                        else:
                            mail_id_list.append(mail_id)
                    else:
                        mail_id_list.append(mail_id)

                df['Mail_ID'] = mail_id_list

                apollo_driver.quit()
                st.table(df)
                csv_data = df.to_csv(index=False).encode()
                file_name = f'{(file.name).replace(".xlsx","")}_with_mails.csv'
                with col1:
                    pass
                with col2:
                    pass
                with col3:
                    st.write(" ")
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=file_name,
                        mime='text/csv'
                    )
                with col4:
                    pass
                with col5:
                    pass


