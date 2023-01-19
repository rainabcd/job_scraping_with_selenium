import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

# provide driver's path and run Chrome
path = '/chromedriver'
driver = webdriver.Chrome(path)

# maximize the window
driver.maximize_window()

# go to the login page
driver.get('https://www.linkedin.com/login');
time.sleep(1)

# input login info
user_name = "rainakwan@gmail.com"  # First line
password = "27297829"  # Second line
driver.find_element(By.NAME, 'session_key').send_keys(user_name)
driver.find_element(By.NAME, 'session_password').send_keys(password)
time.sleep(1)

# click button to login
driver.find_element(By.CLASS_NAME, 'login__form_action_container ').click()

# go to the search result page with filters applied
search_result = "https://www.linkedin.com/jobs/search?keywords=Data Analysis&location=Canada&locationId=&geoId=101174742&f_TPR=&f_E=2,3&f_WT=2&position=1&pageNum=0"
driver.get(search_result)
time.sleep(1)

# links to be visited
links = []

try:
    for page in range(2, 42):
        time.sleep(2)
        # define the block with all jobs
        jobs_block = driver.find_element(By.CLASS_NAME, 'jobs-search-results-list')
        # all jobs in the jobs block
        jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

        for job in jobs_list:
            # find links of each job by tag name
            all_links = job.find_elements(By.TAG_NAME, "a")
            for a in all_links:
                # append the link to links list if it is not added to list yet
                if a.get_attribute('href') not in links:
                    links.append(a.get_attribute('href'))
                else:
                    pass
            # scroll down til the end of the job element
            driver.execute_script("arguments[0].scrollIntoView();", job)

        print(f"Scraped {len(links)} jobs in {page - 1} page(s)")
        # go to next page:
        driver.find_element(By.XPATH, f"//button[@aria-label='Page {page}']").click()
        time.sleep(3)
except:
    pass

print(f'Finish crawling {len(links)} job URLs.')

job_urls = []
job_titles = []
company_names = []
recency = []
job_types = []
job_desc = []
i = 0
j = 1

for i in range(len(links)):
    try:
        driver.get(links[i])  # visit each link
        job_urls.append(links[i])  # save the link in list
        i += 1
        time.sleep(1)
        # click see more for jd
        driver.find_element(By.CLASS_NAME, 'artdeco-card__actions').click()
        time.sleep(2)

    except:
        pass

    # scrape general info about the job
    contents = driver.find_elements(By.CLASS_NAME, 'p5')
    for content in contents:
        try:
            job_titles.append(content.find_element(By.TAG_NAME, "h1").text)
            company_names.append(content.find_element(By.XPATH,
                                                      "/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[1]/span[1]/a").text)
            recency.append(content.find_element(By.XPATH,
                                                "/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[1]/span[2]/span[1]").text)
            job_types.append(content.find_element(By.XPATH,
                                                  "/html/body/div[5]/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[1]/div[2]/ul/li[1]/span").text)

        except:
            pass
        time.sleep(2)

    job_description = driver.find_elements(By.CLASS_NAME, 'jobs-description__content')
    for description in job_description:
        job_text = description.find_element(By.CLASS_NAME, "jobs-box__html-content").text
        job_desc.append(job_text)
        print(f'Scraping the Job Offer {j}')
        time.sleep(2)
    j += 1

# # test to see if data is successfully scraped
# print(job_titles, company_names, post_dates, job_types)

# create a dataframe to store scraped job info
jobs_tuples = list(zip(job_urls, job_titles, company_names, recency, job_types, job_desc))
jobs_df = pd.DataFrame(jobs_tuples,
                       columns=['job_url', 'job_title', 'company_name', 'recency', 'job_type', 'job_desc'])
# add scraped date as reference
today = datetime.today().strftime("%d-%m-%Y")
jobs_df['date_scraped'] = today

# store data as csv for further steps
jobs_df.to_csv(f'job_info_{today}.csv', index=False)