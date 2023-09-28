import requests
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep
from os.path import isfile,join
import pickle
from bs4 import BeautifulSoup
import argparse
from getpass import getpass


IMDB_HOME_URL = r'https://www.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl91cyIsInJlZGlyZWN0VG8iOiJodHRwczovL3d3dy5pbWRiLmNvbS8_cmVmXz1sb2dpbiJ9&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&tag=imdbtag_reg-20'
SEARCH_PAGE = 'https://www.imdb.com/'

class AlreadyVotedError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)



def search_movie(driver, movie_title='', movie_year=''):
    # Go to search page
    driver.get(SEARCH_PAGE)
    
    # Search movie
    search_bar = driver.find_element(value='suggestion-search').send_keys(movie_title + ' ' + movie_year)
    seearch_button = driver.find_element(value='suggestion-search-button').click()
    
    # Get first result 
    results = driver.find_element(by=By.CLASS_NAME, value="ipc-metadata-list-summary-item__t")
    
    # Get link from first result
    link = results.get_attribute('href')
    return link
    
    

def set_movie_score(driver, movie_link, score):
    
    # Access movie link
    driver.get(movie_link)
    
    # Wait for page to load 
    #(also avoid excess of request that would kick out of the webpage)
    sleep(2)
    
    # Check if already voted. If so, skip raising AlreadyVotedError()
    
    try:
        # Get poster element
        xpath_poster = f"//section[@data-testid='atf-wrapper-bg']"
        poster = driver.find_element(by=By.XPATH, value=xpath_poster)
        
        # Get poster HTML 
        html_poster = poster.get_attribute('outerHTML')
        soup = BeautifulSoup(html_poster, 'html.parser')
        
        # Check if already rated element is present
        aria_label_already_voted = f'Your rating: {score}'
        specific_div = soup.find("button", {"aria-label": aria_label_already_voted}, recursive=True)
        if specific_div is not None:
            raise AlreadyVotedError(f'Already voted for movie ')
    
    except AlreadyVotedError as e:
        raise e
    except selenium.common.exceptions.NoSuchElementException:
        pass
    
    # Find and click rate button
    starts_with_text = "Rate "
    xpath_expression_rate_button = f"//*[starts-with(@aria-label, '{starts_with_text}')]" 
    rate_button = driver.find_element(by=By.XPATH, value=xpath_expression_rate_button).click()
    
    # Then appear transition to stars count
    aria_label_score_button = f'Rate {score}'
    xpath_expression_score_button = f"//*[@aria-label='{aria_label_score_button}']"
    
    # Remove overlay element that blocks the score button
    try:
        overlay_element = driver.find_element(By.CLASS_NAME, "ipc-starbar__touch")
        # Use JavaScript to remove the overlay element from the DOM
        driver.execute_script("arguments[0].remove();", overlay_element)
    except selenium.common.exceptions.NoSuchElementException:
        print("Overlay element not found. Going directly to click button")

    # Click the score element
    score_star = driver.find_element(By.XPATH, xpath_expression_score_button).click()
    
    # Click submit rate
    submit_rate_button_class_name = "ipc-rating-prompt__rate-button"
    button_element = driver.find_element(By.CSS_SELECTOR, f"[class*='{submit_rate_button_class_name}']").click()


def main(id, chromedriver_path):
    
    # Get filenames
    votes_json_file =  f'votes_user_{id}.json'
    already_voted_pkl = f'already_voted_{id}.pkl'
    missing_movies_pkl = f'missing_movies_{id}.pkl'
    
    # Load votes from json file
    with open(votes_json_file, 'r') as file:
        votes_dict = json.load(file)
        
    # Load Chrom driver
    service = Service(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    
    # IMDB credential details
    USERNAME = input('Insert IMDB email: ')
    PASSWORD = getpass('Insert IMDB password: ')
    
    
    driver.get(IMDB_HOME_URL)
    # Login
    driver.find_element(value='ap_email').send_keys(USERNAME)
    driver.find_element(value='ap_password').send_keys(PASSWORD)
    driver.find_element(value='a-autoid-0').click()


    already_voted = [] # Used if reexecuted to avoid duplication of work
    missing_movies = [] #saved in Pickle to know unsuccessful cases
    # Load pickle if second or third execution
    if isfile(already_voted_pkl):
        already_voted = pickle.load(open(already_voted_pkl, 'rb'))
        
    for idx, (key, movie_info) in enumerate(votes_dict.items()):
        print(idx)
        
        # Get data from votes_dict
        title = movie_info['title']
        score = movie_info['score']
        year = movie_info['year']
        
        # Check if already voted
        if key in already_voted:
            print(f'ALREADY VOTED - {title} - {score}')
            continue

        # Access movie link
        try:
            movie_link = search_movie(driver, title, year)
        except Exception as e: 
            print(f'ERROR - NO DISPONIBLE - {title} - {score}')
            missing_movies += [key]
            continue
        
        # Set score to movie
        try:
            set_movie_score(driver, movie_link, score)
            print(f'SUCCESS - {title} - {movie_link} - {score}')
            already_voted += [key]
        except AlreadyVotedError as e:
            print(f'ALREADY VOTED - {title} - {movie_link} - {score}')
            already_voted += [key]
        except Exception as e: 
            print(f'ERROR - {title} - {movie_link} - {score}') 
            missing_movies += [key]
            # print(e)
        
            
        pickle.dump(already_voted, open(already_voted_pkl, 'wb'))
        pickle.dump(missing_movies, open(missing_movies_pkl, 'wb'))
    

def load_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-i','--id',
        required=True, 
        help='User id from FilmAffinity URL'
    )
    argparser.add_argument(
        '-c','--chromedriver',
        required=False,
        default='chromedriver',
         help='Path to chromedriver executable'
    )
    args =  argparser.parse_args()
    return args
    
if __name__ == '__main__':
        
    args = load_args()
    votes_json_file = f'votes_user_{args.id}.json'
    main(args.id, args.chromedriver)  



