import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import csv


# Global variable for Men's URL
URL_MEN = "https://volleybox.net/players/ranking"

# Global variable for Women's URL
URL_WOMEN = "https://women.volleybox.net/players/ranking"


# Initialize browser
def init_browser(URL):
    print("Initializing webdriver")
    driver = webdriver.Chrome()
    driver.get(URL)
    return driver

# Scroll to the end of page until no new spans are found
def scroll_to_end_of_page(driver):
    print("Grabbing spans")
    num_spans_before = 0

    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down in steps
        for _ in range(0, last_height + 100, 100):  # Here, 100 is the step size
            driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(0.1)  # Adjust this delay for smoother scrolling
        
        # Check the new scroll height after the above scrolling
        new_height = driver.execute_script("return document.body.scrollHeight")

        spans = driver.find_elements(By.CSS_SELECTOR,'span.title')
        if len(spans) == num_spans_before or num_spans_before >= 400:
            break
        num_spans_before = len(spans)

# Extract player details from a given URL
def extract_player_data(name, points, idx):
    player_data = {}
    query = name + " volleybox"
    google_url = f"https://www.google.com/search?q={query}"
    response = requests.get(google_url)
    soup = BeautifulSoup(response.content, 'lxml')
    results = soup.find_all('a', href=True)
    first_result_url = None
    for result in results:
        url = result['href']
        start_idx = url.find('https://')
        end_idx = url.find('&', start_idx)
        if start_idx != -1:
            if end_idx != -1:
                url = url[start_idx:end_idx]
            else:
                url = url[start_idx:]
            
    
            # Check if URL is an image
            if url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')):
                continue
            
            if "volleybox.net" in url:
                first_result_url = url
                break

    if first_result_url:
        # Fetch and parse the first result (you can also use Selenium if JavaScript loading is required)
        try:
            response = requests.get(first_result_url)

        #Getting the information from Volleybox
         # You can log additional details or take other actions here if needed
            soup = BeautifulSoup(response.content, 'lxml')
            with open('output.html', 'w', encoding='utf-8') as file:
                file.write(soup.prettify())

            # Extract the contents of the <dl> tag
            dl_contents = soup.find('dl')
            player_data = {}
            #cm, kg, 
            if dl_contents:
                terms = dl_contents.find_all('dt')
                descriptions = dl_contents.find_all('dd')

                for term, description in zip(terms, descriptions):
                    # term.get_text(strip=True), Height, Weight
                    _text = description.get_text(strip=True)
                    #Making it check ALL the strings. 
                    _text = _text.replace("kg", "").replace("cm", "").strip()
                    if term.get_text(strip=True) == "Nationality":
                        _text = _text.split(",")[0] #usa, italy -> ['usa', 'italy']
                    player_data[term.get_text(strip=True)] = _text

            else:
                print(f"No <dl> element found for {name}.")
            
            # Extracting awards, tournaments, and matches
            span_elements = soup.find_all('span')

            # Filter spans that contain a var child and extract data
            count = 0
            for span in span_elements:
                var_element = span.find('var')
                if var_element:  # Check if var element exists inside the span
                    key = span.text.replace(var_element.text, '').strip()  # Get the text of the span excluding the var text
                    if key == 'Awards':
                        player_data['Awards'] = var_element.text
                        count+=1

                    if key == 'Tournaments':
                        player_data['Tournaments'] = var_element.text
                        count+=1

                    if key == 'Matches':
                        player_data['Matches'] = var_element.text
                        count+=1
                if count == 3:
                    break
        
            # Add the points data
            player_data['Points'] = points[idx].split(" ")[0]
            
        except requests.exceptions.ConnectionError:
                print("A connection error occurred. Skipping...")

    return player_data

# Save data to CSV file
def save_to_csv(players_data):
    headers = set()
    for player, data in players_data.items():
        headers.update(data.keys())
    headers = ["Name"] + list(headers)

    with open('./data/players_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for name, data in players_data.items():
            data["Name"] = name
            writer.writerow(data)


def main(url):
    driver = init_browser(url)
    scroll_to_end_of_page(driver)

    names = [span.text for span in driver.find_elements(By.CSS_SELECTOR, 'span.title')]
    points = [span.text for span in driver.find_elements(By.CSS_SELECTOR, 'span.bolded-points')]
    driver.quit()

    total_names = len(names)
    players_data = {}

    for idx, name in enumerate(names):
        print(f"Currently processing: {idx}/{total_names}")
        player_data = extract_player_data(name, points, idx)
        players_data[name] = player_data

    save_to_csv(players_data)
    print("Data saved to players_data.csv")

if __name__ == "__main__":
    # Setting up argument parsing
    parser = argparse.ArgumentParser(description="Fetch volleyball player rankings from volleybox.net")
    parser.add_argument('-w', '--women', action='store_true', help="Use the women's ranking URL")
    args = parser.parse_args()

    # Choose the URL based on the provided flag
    url_to_use = URL_WOMEN if args.women else URL_MEN
    
    main(url_to_use)
