import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import pandas as pd
import dateparser

# Define an empty DataFrame
# Keyword is the keyword used in Google search. Rest of df items are extracted from Medium articles
df = pd.DataFrame(columns=['Keyword', 'URL', 'Title', 'Subtitle', 'Summary', 'Reactions', 'MemberOnly', 'Date'])

# Open the Chrome browser
driver_service = Service(r"Path to chromedriver.exe")
options = Options()
driver = webdriver.Chrome(service=driver_service, options=options)
wait = WebDriverWait(driver, 10)


# Define the Google search URL
base_url = 'https://www.google.com/search?q=site%3Amedium.com+'
search_keywords = ["copilot", "codewhisperer", "tabnine", "chatgpt", "ai code assistants"]


# Get the URLs of the search results
urls = set()

# Set the maximum number of clicks of "more results" on the Google search page
max_clicks = 10 # increase variable to get more results


# Iterate over search keywords
for keyword in search_keywords:
    url = base_url + keyword
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    prev_urls_count = len(urls)  # Count of urls before new keyword

    clicks = 0  # initialize the counter

    while clicks < max_clicks:
        
        # Scroll down to bottom multiple times
        for _ in range(10):  # any number >= actual number of scrolls needed will yield all results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(3)  

        # Find the search result links
        link_elements = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a')

        # Add the URLs to the set
        for link in link_elements:
            urls.add(link.get_attribute('href'))

        # try to click the more results or next page button, check the results page to see which one you need
        try:
            next_button = driver.find_element(By.XPATH, "//span[contains(text(), 'More results')]")
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            driver.execute_script("arguments[0].click();", next_button)
            clicks += 1
        except NoSuchElementException:
            print('No more pages')
            break

        # Wait for the next page to load
        time.sleep(5)
    
    print(f'Added {len(urls) - prev_urls_count} urls for keyword: {keyword.replace("+", " ")}')


    # Iterate over each URL, navigate to it and then extract the article details
    for url in urls:
        driver.get(url)
        time.sleep(5)  # wait for the page to load
    
        try:
            # get the article title
            title_element = driver.find_element(By.XPATH, "//h1[contains(@class, 'pw-post-title')]")
            title = title_element.text
        except NoSuchElementException:
            title = None
    
        try:
            # get the article subtitle
            subtitle_element = driver.find_element(By.XPATH, "//h2[contains(@class, 'pw-subtitle-paragraph')]")
            subtitle = subtitle_element.text
        except NoSuchElementException:
            subtitle = None
    
        try:
            # get the article summary
            summary_element = driver.find_element(By.XPATH, "//p[contains(@class, 'pw-post-body-paragraph')]")
            summary = summary_element.text
        except NoSuchElementException:
            summary = None
    
        try:
            # get the reactions
            reactions_element = driver.find_element(By.XPATH, "//div[contains(@class, 'pw-multi-vote-count')]") 
            reactions = reactions_element.text
        except NoSuchElementException:
            reactions = None
                
        try:
            # Check if 'Member-only story' is in the HTML
            driver.find_element(By.XPATH, "//*[contains(text(), 'Member-only story')]")
            member_only = True
        except NoSuchElementException:
            member_only = False

        try:
                subtitle_element_l = driver.find_elements(By.CLASS_NAME, "pw-subtitle-paragraph")
                title_element_l = driver.find_elements(By.CLASS_NAME, "pw-post-title")
            
                if subtitle_element_l:
                    info_div = subtitle_element_l[0].find_element(By.XPATH, "..")
                elif title_element_l:
                    info_div = title_element_l[0].find_element(By.XPATH, "..")
                else:
                    info_div = driver.find_elements(By.CLASS_NAME, "speechify-ignore")[-1]
            
                info_div = info_div.find_element(By.CLASS_NAME, "ae")
                date_text = info_div.find_elements(By.TAG_NAME, "span")[-1].text
            
                if date_text == "·":
                    raw_rdate = info_div.text.split("\n")[-1]
                    date = dateparser.parse(raw_rdate)  # use dateparser to parse the relative date
                    date = date.strftime("%B %d, %Y")  # format the date as a string
                else:
                    date = dateparser.parse(date_text).strftime("%B %d, %Y")  # parse and format the date
            
        except NoSuchElementException:
                date = None
            
        # Add the data to the DataFrame
        df = df.append({'Keyword': keyword, 'URL': url, 'Title': title, 'Subtitle': subtitle, 'Summary': summary, 'Reactions': reactions, 'MemberOnly': member_only, 'Date'}, ignore_index=True)

# Save the DataFrame to a CSV file
df.to_csv('article_data.csv', index=False)

# Close the browser
driver.quit()
