import streamlit as st

def introduction_panel():
    st.title("Welcome to ProSpektrum!")

    st.write("ProSpektrum offers the ultimate solution for streamlined and precise lead generation. Our tool simplifies the process of identifying & engaging potential clients, making these tasks significantly more efficient.")

    st.markdown("<h4>LinkedIn Scraper</h4>",unsafe_allow_html=True)
    st.write("Extract leads from specific LinkedIn accounts with ease and gives profile scores based on multiple criterias.")
    st.write("Features extracted includes:")
    st.write("1. Employee Name")
    st.write("2. Current Organization")
    st.write("3. Designation")
    st.write("4. About Section")
    st.write("5. Role Description")
    st.write("6. Last 3 activities on LinkedIn")
    st.write("Based on the above mentioned features scores for each profile will be given. Which makes it easy for Sales team to fetch list of peoples to be targeted in a particular company!")
    st.markdown("<h4>Apollo Scraper</h4>",unsafe_allow_html=True)
    st.write("Verifies emails directly from the Apollo site, ensuring data accuracy and reliability.")
