# Importing Required Modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pandas as pd
import os
from tqdm import tqdm
import gc
import time
from tqdm import tqdm
import traceback
import yaml
import random
import re
from io import BytesIO
from fuzzywuzzy import fuzz
import warnings
warnings.filterwarnings('ignore')
from Bots.apollo_scraper_bot import apollo_driver_setup,fetch_mail_from_apollo

# Function which fetches the config file from the directory
def fetch_config(): 
    with open(os.path.join(os.path.dirname(os.getcwd()),'Config','filters_config.yaml'), 'r') as file:
        config = yaml.safe_load(file)
    return config

# Function which creates a driver for Linkedin
# Logs in using different driver for each session to prevent bot detection
def driver_setup():
    '''Drivers used = Chrome, ChromiumEdge, Microsoft Edge'''
    random_driver = int(random.uniform(1,3))
    if random_driver == 1:
        try:
            driver = webdriver.Chrome()
        except:
            driver = webdriver.Chrome(ChromeDriverManager().install())
    elif random_driver == 2:
        try:
            driver = webdriver.Edge()
        except:
            driver = webdriver.Edge(EdgeChromiumDriverManager().install())
    driver.delete_all_cookies()
    driver.get("https://linkedin.com")
    driver.maximize_window()
    driver.implicitly_wait(3)
    time.sleep(random.uniform(2,4))
    return driver

# Function which initializes the session for scraping a particular account
def initialize_session(driver, linkedin_username, linkedin_password, company_name):
    username = driver.find_element(By.NAME, 'session_key')
    password = driver.find_element(By.NAME, 'session_password')
    wait = WebDriverWait(driver, 20)
    signin_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in')]")))
    
    # Passing Credentials to respective fields
    username.send_keys(linkedin_username)
    password.send_keys(linkedin_password)
    signin_button.click()
    time.sleep(random.uniform(3,4))

    # Opening Sales Navigator
    driver.get('https://www.linkedin.com/sales/home')

    # Passing name of the account to be scraped
    time.sleep(random.uniform(4,6))
    driver.find_element(By.ID,'global-typeahead-search-input').send_keys(company_name)
    driver.find_element(By.ID,'global-typeahead-search-input').send_keys(Keys.ENTER)
    time.sleep(random.uniform(2,4))

    # Expanding collapsed tab
    driver.find_element(By.XPATH,'//button[@aria-label="Expand filter panel"]').click()
    time.sleep(random.uniform(0.4,0.8))
    return driver

# Function which adds current company in the Company filter
def current_company_filter(driver,company_name):
    '''company_name = Company name which needs to be considered'''
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[1].click()
    time.sleep(random.uniform(1.5,2.0))
    driver.find_element(By.CLASS_NAME,'artdeco-typeahead__input').send_keys(company_name)
    time.sleep(random.uniform(1.5,2.0))
    try:
        driver.find_elements(By.XPATH, f'//*[contains(@aria-label,"Include")]')[0].click()
    except:
        driver.find_element(By.CLASS_NAME,'artdeco-typeahead__input').send_keys(Keys.ENTER)
    time.sleep(random.uniform(1.5,2.0))
    return driver

# Function which adds geography in the Geography filter
def geography_filter(driver,geography):
    '''geography = Country or City which needs to be considered'''
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[13].click()
    time.sleep(random.uniform(1.5,2.0))
    driver.find_element(By.CLASS_NAME,'artdeco-typeahead__input').send_keys(geography)
    time.sleep(random.uniform(1.5,2.0))
    driver.find_element(By.CLASS_NAME,'artdeco-typeahead__result').click()
    time.sleep(random.uniform(1.5,2.0))
    return driver

# Function which adds Years of Experience in the corresponding filter
def years_of_experience_filter(driver):
    '''Years of Experience will be default 'More than 10 years' for all the accounts'''
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[15].click()
    time.sleep(random.uniform(1.5,2.0))
    driver.find_element(By.XPATH,'//*[text()="More than 10 years"]').click()
    time.sleep(random.uniform(1.5,2.0))
    return driver

# Function which adds roles of decision makers to the Seniority filter
def seniority_level_filter(driver,config):
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[8].click()
    time.sleep(random.uniform(1.5,2.0))
    seniority_level = config['seniority_level_filter']
    for level in seniority_level:
        driver.find_element(By.XPATH, f'//*[contains(@aria-label,"{level}")]').click()
        time.sleep(random.uniform(0.5,1))
    return driver

# Function which adds functions to be considered to the filter
def functions_filter(driver,config):
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[7].click()
    time.sleep(random.uniform(3,6))    
    functions_considered = config['functions_filter']
    for function in functions_considered:
        driver.find_element(By.XPATH, f'//*[contains(@aria-label,"{function}")]').click()
        time.sleep(random.uniform(0.5,1.0))
    return driver

# Function which adds industries which needs to be excluded to Industries filter
def exclude_industries_filter(driver,config):
    driver.find_elements(By.CLASS_NAME,'artdeco-button__icon')[14].click()
    time.sleep(random.uniform(2,3))
    industries_to_exclude = config['exclude_industries_filter']

    for industry in industries_to_exclude:
        target_label = f'Exclude “{industry}'
        driver.find_element(By.XPATH, f'//*[contains(@aria-label, "{target_label}") and contains(@aria-label, "Industry filter")]').click()
        time.sleep(random.uniform(1,1.5))
        
    driver.find_element(By.XPATH,'//*[@aria-label="Collapse filter panel"]').click()
    time.sleep(random.uniform(2,2.5))
    return driver

# Function which obtains Profile links of the people available and return the list
def profile_links_scraper(driver):
    search_results_container = driver.find_element(By.ID,'search-results-container')
    master_profile_links,page = [],1
    temp_button = driver.find_elements(By.XPATH, f'//button[contains(@aria-label,"Next")]')
    if len(temp_button)>0:
        while True:
            search_results_container = driver.find_element(By.ID,'search-results-container')
            time.sleep(random.uniform(3, 3.5))
            for i in range(1,42):
                driver.execute_script("arguments[0].scrollTo(0, arguments[1]);", search_results_container,100*int(random.uniform(i-2,i+2)))
                time.sleep(random.uniform(0.2, 0.4))
            time.sleep(random.uniform(2, 2.5))
            scroll_panel = driver.find_elements(By.CLASS_NAME, 'artdeco-entity-lockup')
            profile_links = [link.find_element(By.TAG_NAME, 'a').get_attribute('href') for link in scroll_panel]
            master_profile_links.append(profile_links)
            time.sleep(random.uniform(2.5, 3.5))
            next_button = driver.find_element(By.XPATH, f'//button[contains(@aria-label,"Next")]')
            if next_button.is_enabled():
                next_button.click()
                time.sleep(random.uniform(2.5, 3.5))
                page = page + 1
            else:
                break
    else:
        search_results_container = driver.find_element(By.ID,'search-results-container')
        time.sleep(random.uniform(3,3.5))
        for i in range(1,42):
            driver.execute_script("arguments[0].scrollTo(0, arguments[1]);", search_results_container,100*int(random.uniform(i-2,i+2)))
            time.sleep(random.uniform(0.2, 0.4))
        time.sleep(random.uniform(1.8,2.2))
        scroll_panel = driver.find_elements(By.CLASS_NAME, 'artdeco-entity-lockup')
        profile_links = [link.find_element(By.TAG_NAME, 'a').get_attribute('href') for link in scroll_panel]
        master_profile_links.append(profile_links)
        time.sleep(random.uniform(2.5, 3.5))
    profile_list = [link for link_list in master_profile_links for link in link_list]
    return profile_list

# Master function which makes use of all filter functions to create list of profile links
def final_lead_scraper(linkedin_username, linkedin_password, company_name, geography):
    config = fetch_config()
    driver = driver_setup()
    print("Driver created Successfully!")
    driver = initialize_session(driver, linkedin_username, linkedin_password, company_name)
    print("Session initialized Successfully!")
    driver = current_company_filter(driver,company_name)
    print("Company filter applied Successfully!")
    driver = geography_filter(driver,geography)
    print("Geography filter applied Successfully!")
    driver = years_of_experience_filter(driver)
    print("YOE filter applied Successfully!")
    driver = seniority_level_filter(driver,config)
    print("Seniority filter applied Successfully!")
    driver = functions_filter(driver,config)
    print("Functions filter applied Successfully!")
    driver = exclude_industries_filter(driver,config)
    print("Exclude industries filter applied Successfully!")
    profile_list = profile_links_scraper(driver)
    print("Profile links scraped Successfully!")
    return profile_list,driver

# Function which cleans the name and removes all sort of foreign characters 
def name_cleaner(name):
    clean_list = ['(he/him/his)','(he/him)','(He/Him)','(He/Him/His)','(She/Her)','(she/her)']
    for element in clean_list:
        name = name.replace(element,'')
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    name = name.split(',')[0].strip()
    return name

def is_word_in_text(text, target_word, threshold=80):
    similarity_score = fuzz.partial_ratio(text.lower(), target_word.lower())
    return similarity_score >= threshold

# Function which post process the leads data which is generated, it removes the leads which has designations which are not required
def leads_post_processing(df, company_name):

    # Roles which contains below mentioned keywords needs to be ignored
    roles_to_be_ignored = ['HR','Human Resource','Talent Acquisition','L&D','Learning & Development',
                        'Learning','BDM','Business Development Manager','Legal','Affairs','Sustainability',
                        'Regional','Compliance','Zonal','Zone','Audit','Store Manager','Customer Success Lead',
                        'Buyer','Owner','Seller','Asset','Learning','UX','UI','Risk','Construction','Sales Person',
                        'Salesperson','Strategic Partnership','Support','Supervisor','Education','Environment','Planner'
                        'Manager','Distribution','Specialist','Planner','Designer','Store','Stores','Paid','Jewellery',
                        'Business','Managers','Manager','Design','User Experience','User Interface','UI/UX'
                        'Leader','Governance','Principal','Insurance','Retired','Member','Beauty','Quality Assurance','Keyholder',
                        'Key Holder','Gift','Facility','Shortage','Crime','Energy','Analyst','Culinary','Loss','People',
                        'Public Relationship','Public Relation','Security','Tax','Project','Staff','Consultant','Artist',
                        'Treasury','Allocation','Corporate']
    
    designation_list = df['Designation'].to_list()
    flag_list = []

    # Comparing all the designations with the keywords and removing the one which matches any of the keywords
    for i,designation in enumerate(designation_list,start = 0):
        check_list = [designation for key in roles_to_be_ignored if designation.lower().find(key.lower())!= -1]
        if len(check_list)>0:
            flag_list.append(i)
            
    filtered_df = df[~df.index.isin(flag_list)]
    filtered_df['Flag'] = filtered_df['Current_company'].apply(lambda x:is_word_in_text(x,company_name,threshold=80))
    filtered_df = filtered_df[filtered_df['Flag'] == True]
    filtered_df.drop("Flag",axis = 1, inplace = True)
    return filtered_df.reset_index(drop = True)
    
# Function which generates a file which has details of employees available in the account provided
def mass_mailing_leads_generator(driver,profile_links):
    '''profile_links = List which has URLs of employees available in an organization after applying series of filters'''
    '''Profile mining will be done in matches. For single batch there will be 10 profiles'''
    # Defining empty list for storing employee details, profile at which error occured, error occured, error details
    master_profiles, error_profile, errors_list, error_traceback_list = [[],[],[],[]]
    profile_link_batches = [profile_links[i:i+10] for i in range(0, len(profile_links), 10)]
    print(f"Total number of profiles {len(profile_links)}")
    for i,batch in enumerate(profile_link_batches, start = 1):
        for profile in tqdm(batch, desc = f'Batch {i} Profiles Scraped'):
            gc.collect()
            try:
                driver.get(profile)
                time.sleep(random.uniform(2.8,3.3))
                # Locating About section in the profile and fetching details from there
                try:
                    about_section = driver.find_element(By.ID,'about-section')
                    show_more_button = about_section.find_element(By.XPATH, './/*[contains(@class, "_ellipsis-button_") and contains(@class, "_unstyled-button_")]')
                    show_more_button.click()
                    replace_contents = ['\n','\t','About','Show less']
                    about = about_section.get_attribute('textContent').strip()
                    for element in replace_contents:
                        about = about.replace(element,' ')
                except:
                    about = 'No About Section'

                # Fetching employee name
                employee_name = driver.find_element(By.XPATH, '//*[contains(@class, "_name-title-container_")]').get_attribute('textContent').strip().split("\n")[0]

                # Fetching list of companies he worked for
                list_of_companies = driver.find_elements(By.XPATH, '//*[contains(@class, "_experience-entry_")]')

                # Fetching current company he is working in
                current_company  = list_of_companies[0].find_element(By.TAG_NAME,'img').get_attribute('title')

                # Fetching Designation of the employee
                try:
                    current_designation = list_of_companies[0].find_elements(By.TAG_NAME, 'h3')[0].get_attribute('textContent').strip()
                except:
                    current_designation = list_of_companies[0].find_elements(By.TAG_NAME, 'h2')[0].get_attribute('textContent').strip()

                # Checking if there are any Description given in the experience profile and fetching it
                try:
                    roles_in_cc = list_of_companies[0].find_elements(By.TAG_NAME, 'h3')
                except:
                    roles_in_cc = list_of_companies[0].find_elements(By.TAG_NAME, 'h2')
                if len(roles_in_cc) > 1:
                    try:
                        role_description = list_of_companies[0].find_elements(By.XPATH, './/*[contains(@class, "_multi-position-description_")]')[0].get_attribute('textContent')
                    except:
                        role_description = 'No Description'
                else:
                    try:
                        role_description = list_of_companies[0].find_elements(By.XPATH, './/*[contains(@class, "_single-position-description_")]')[0].get_attribute('textContent')
                    except:
                        role_description = 'No Description'

                # Locating Activity status block and fetching recent activities of the employee in LinkedIn
                activity_status_elements = driver.find_elements(By.XPATH, '//*[contains(@class, "_recent-activities-item_")]')
                try:
                    latest_activity = [activity_element.find_element(By.TAG_NAME,'time').get_attribute('textContent').replace('ago','').strip() 
                                    for activity_element in activity_status_elements]
                    latest_activity = '-'.join(latest_activity)
                except:
                    latest_activity = 'No activities logged'
                employee_profile = [employee_name,current_company,current_designation,about,role_description,profile,latest_activity]
                master_profiles.append(employee_profile)
                time.sleep(random.uniform(0.3,0.7))
            except Exception as e:
                # Capturing error tracebacks and appending to the respective list
                error_traceback_list.append(traceback.format_exc())
                error_profile.append(profile)
                errors_list.append(e)
        time.sleep(random.uniform(1,1.5))

    # Creating a DataFrame named employees_df which consists of Employee's name, Current company etc.,
    employees_df = pd.DataFrame(master_profiles, columns = ['Employee_name','Current_company','Designation','About',
                                                            'Role Description','Profile Link','Activity_status'])

    # Cleaning the names which are scraped from the LinkedIn
    employees_df['Employee_name'] = employees_df['Employee_name'].apply(lambda x:name_cleaner(x))

    # Creating a DataFrame named error_df which has details of error occured to make the debugging easier
    error_df = pd.DataFrame({'Profile':error_profile,'Error':errors_list,'Traceback':error_traceback_list})

    return employees_df,error_df

# Function which checks the activeness of employee on LinkedIn based on Post, Comments or Shares he did.
def active_flag(activity_status_list):
    activity_status_list = activity_status_list.split('-')
    active_bucket = [f'{i}m' for i in list(range(0,60))] + [f'{i}h' for i in list(range(0,24))] + [f'{i}d' for i in list(range(0,31))] + ['1w','2w','3w','4w','1mo']
    activity_flags = [1 if status in active_bucket else 0 for status in activity_status_list]
    if sum(activity_flags) > 0:
        return 'Active'
    else:
        return 'Non Active'

# Function which checks whether the employee has updated his about section
def about_flag(about):
    if len(about) > 50:
        return 'Updated'
    else:
        return 'Not Updated'

# Function which checks whether the role description is provided under the role he is working
def role_description_flag(role_description):
    if len(role_description) > 30:
        return 'Updated'
    else:
        return 'Not Updated'

# Function which flags whether the profile is eligible for customized mails or not based on multiple conditions
def customization_flag(flag_list):
    if flag_list == ['Active','Updated','Updated']:
        return 'Approved'
    elif flag_list == ['Non Active','Updated','Updated']:
        return 'Consider'
    else:
        return 'Not Approved'

# Master function which makes use of all flag functions and generates the result files
def profile_scoring(mass_mail_df):
    mass_mail_df['Activity_Flag'] = mass_mail_df['Activity_status'].apply(lambda x: active_flag(x))
    mass_mail_df['About_Flag'] = mass_mail_df['About'].apply(lambda x:about_flag(x))
    mass_mail_df['JD_Flag'] = mass_mail_df['Role Description'].apply(lambda x:role_description_flag(x))
    mass_mail_df['Customization_Flag'] = mass_mail_df.apply(lambda x:customization_flag([x['Activity_Flag'],x['About_Flag'],x['JD_Flag']]), axis = 1)
    return mass_mail_df

# Function which stores the final workbook in Bytes in order to store it in Code Bytes memory in order to avoid creating temporary files on disk
def create_excel_bytes(df_list, sheet_name_list):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for i in range(len(df_list)):
            df_list[i].to_excel(writer, sheet_name=sheet_name_list[i], index=False)
    output.seek(0)
    return output

# Final Function called Lead Gen Accelerator which will be used in main script
def lead_gen_accelerator(linkedin_username, linkedin_password, company_name, geography):
    start_time = time.time()
    try:
        profile_links,driver = final_lead_scraper(linkedin_username, linkedin_password, company_name, geography)
        mass_mail_df, error_df = mass_mailing_leads_generator(driver,profile_links)
        copy_df = mass_mail_df.copy()
        imp_leads = leads_post_processing(copy_df, company_name)
        copy_df = imp_leads.copy()
        os.makedirs(os.path.join(os.getcwd(),'Error Logs'), exist_ok = True)
        os.makedirs(os.path.join(os.getcwd(),'Exported Leads'), exist_ok = True)
        
        final_scored_df = profile_scoring(copy_df)
        filtered_df = final_scored_df[final_scored_df['Customization_Flag'].isin(['Approved','Consider'])]

        time.sleep(random.uniform(2,3))
        df_list = [mass_mail_df, imp_leads, final_scored_df, filtered_df]
        sheet_name_list = ['All_leads', 'Filtered_leads', 'Flagged_leads', 'Customization_leads']
        excel_data = create_excel_bytes(df_list, sheet_name_list)

        end_time = time.time()
    except Exception as e:
        print("Error",e)
        print(fr"An unexpected error occurred.")
        end_time = time.time()
        print(f"Total time took in minutes - {round((end_time-start_time)/60,2)}")
    return excel_data