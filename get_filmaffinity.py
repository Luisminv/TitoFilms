import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
from time import sleep
import argparse

def main(user_id):
    
    votes_json_file = f'votes_user_{user_id}.json'
    votes_dict = {}
    session = requests.Session()
    
    page = 1
    # Load all pages of votation until there are not any more
    while(True):
        print(f'Scraping page {page}')
        page_url = f'https://www.filmaffinity.com/es/userratings.php?user_id={user_id}&p={page}&orderby=4'
        
        #TODO: CHECK IF WORKS, IT WAS AN INFINITE LOOP
        # Check if page exists
        try:
            response = session.get(page_url)
        except:
            print(f'Page {page_url} does not exist. End of votation measurements')
            break
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fin each vote shown in the page
        votes = soup.find_all('div', class_='user-ratings-movie fa-shadow')
        if len(votes) ==0: 
            print(f'No votes in page {page}. Stopping script')
            
        # Save all votes in JSON file
        for vote in votes: 
            # Get movie title 
            movie_title_obj = vote.find('div', class_='mc-title')
            movie_long_title = movie_title_obj.get_text(strip=True)
            
            # If duplicated
            if movie_long_title in votes_dict.keys():
                print(f'Movie {movie_long_title} already in votes_dict. Skipping')
                continue
            
            # Get movie score 
            movie_score = vote.find('div', class_='ur-mr-rat').get_text(strip=True)
            
            # Get movie link to get rest of info
            movie_link = movie_title_obj.find('a').get('href')
            
            # Go to movie link
            movie_page = session.get(movie_link)
            movie_soup = BeautifulSoup(movie_page.text, 'html.parser')
            
            # Find the "Título original" element
            titulo_original_element = movie_soup.find('dt', text='Título original')
            titulo_original_value = titulo_original_element.find_next_sibling('dd').get_text(strip=True)
            # Sometimes it has "aka" at the end of the title, so we remove it
            titulo_original_value = titulo_original_value[:-4] if titulo_original_value.endswith('aka') else titulo_original_value
            
            # Find the "Año" element
            ano_element = movie_soup.find('dt', text='Año')
            ano_value = ano_element.find_next_sibling('dd').get_text(strip=True)

            # Append to dictionary
            votes_dict[movie_long_title] = {
                'title': titulo_original_value,
                'year': ano_value,
                'score': movie_score,
                'link': movie_link,
                
            }
            
            print(f'Added movie {titulo_original_value} with score {movie_score}')
            # Sleep to avoid being banned from the website for too many requests
            sleep(3)
        
        # Next page
        page += 1
        
        # Save votes to json file after each page
        print(f'Votes dict has {len(votes_dict)} movies')
        with open(votes_json_file, 'w') as file:
            json.dump(votes_dict, file)
        

def load_args():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-i','--id',
        required=True
    )
    args =  argparser.parse_args()
    return args


if __name__ == '__main__':
    
    args = load_args()
    main(args.id)
        