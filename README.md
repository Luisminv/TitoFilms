# FILMAFFINITY TO IMDB

Repository to copy all the movies and series ratings from one or several profiles in FilmAffinity into an IMDB account. Credentials of the FilmAffinity profile are not required, just the ID from the URL such as:

https://www.filmaffinity.com/es/userratings.php?user_id=487295 , where id=487295


# Set up

## Environment

Create a new environment and install the requirements

```
conda create --name <env_name> python=3.10.12
conda activate <env_name>

pip install -r requirements.txt
```


## Selenium and Chromedriver
Download chromedriver version adecuated to your device and chrome version from [here](https://chromedriver.chromium.org/downloads)
Add it to this folder, or if in any other location, add the path to inser_IMDB.py as argument "-c"

# Script execution

1. ```python get_filmaffinity.py -i <user_id>```
   
   Get all the FilmAffinity profile rated films into a .json file

2. ```python insert_IMDB.py -i <user_id> [-c <chromedriver_path>]``` 

   Take every movie from the json file and rate it in the IMDB profile after logging into it.

   It will ask for login credentials during execution.
   
   It just works on accounts that are not linked through Google (as it has an extra layer of security that this script does not cover).
   Sometimes IMDB may ask for No-robot tests, if login does not work, execute code in debug mode with breakpoint after logging in, so if a no-robot task must be made, you can solve it manually through the selenium generated interface. This is usually happeining the first time the script is running
   Sometimes some titles fail unexpectedly, so it is recommended to execute the script several times to ensure all the rates are replicated


# UPDATES

This repository was created for personal purposes and does not have any intention to be maintained.
It is based on both webpages HTML code and URL formatting. Any change in either FilmAffinity.com or IMDB.com could make it crush.
Pull requests for any updates or improvements are welcomed.
Last validation of this repository was 23rd of August
