import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

# Open the Chrome browser
driver_service = Service(r"Path to chromedriver.exe")
options = Options()
driver = webdriver.Chrome(service=driver_service, options=options)
wait = WebDriverWait(driver, 10)

# Define the Google search URL
base_url = 'https://www.google.com/search?q=site%3Amedium.com+'
search_keywords = ["AI+code+assistants", "AI+coding+buddies", "copilot"]

# Get the URLs of the search results
urls = set()

# Iterate over search keywords
for keyword in search_keywords:
    url = base_url + keyword
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    prev_urls_count = len(urls)  # Count of urls before new keyword

    while True:
        # Scroll down to bottom multiple times
        for _ in range(10):  # Increase variable to scroll more times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(3)  # reduced sleep time as we are now scrolling multiple times

        # Find the search result links
        link_elements = driver.find_elements(By.XPATH, '//div[@class="yuRUbf"]/a')

        # Add the URLs to the set
        for link in link_elements:
            urls.add(link.get_attribute('href'))

        # try to click the More Results page button
        try:
            next_button = driver.find_element(By.XPATH, "//span[contains(text(), 'More results')]")
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            driver.execute_script("arguments[0].click();", next_button)
        except NoSuchElementException:
            print('No more pages')
            break

        # Wait for the next page to load
        time.sleep(5)
    
    print(f'Added {len(urls) - prev_urls_count} urls for keyword: {keyword.replace("+", " ")}')

# Iterate over each URL, navigate to it and then extract the article summary and reactions
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

    print(title, subtitle, summary, reactions)

# Close the browser
driver.quit()
