import requests
from bs4 import BeautifulSoup

def fetch_character_names(url="https://www.prydwen.gg/star-rail/characters"):
    """
    Fetches a list of unique character names from the specified URL.

    Args:
        url (str): URL of the page containing character links.

    Returns:
        list: A list of unique character.
        int: HTTP status code of the response.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            base_url = "https://www.prydwen.gg"

            # Extract unique character links
            character_links = {
                base_url + link['href']
                for link in soup.find_all('a', href=True)
                if link['href'].startswith('/star-rail/characters/') and link['href'] != '/star-rail/characters/'
            }

            # Remove base URL from character links
            characters = sorted([link[44:] for link in character_links])

            return characters, response.status_code
        else:
            return [], response.status_code
        
    except requests.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
        return [], None


if __name__ == "__main__":
    # URL of the page with the character list
    url = "https://www.prydwen.gg/star-rail/characters"
    
    character_links, status_code = fetch_character_names(url)

    if status_code == 200:
        print(f'Total characters found: {len(character_links)}')
        print([link.split('/')[-1] for link in character_links])
    else:
        print(f"Error fetching the page, status code: {status_code}")
