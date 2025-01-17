import argparse
from file_io import save_result_to_file
from character_list_parser import fetch_character_links
from character_parser import fetch_character_data_with_selenium

import requests
import time
import os

def process_characters(char_list):
    error_list = []

    for i, char in enumerate(char_list):
        try:
            char_str = f' {char} ({i+1}/{len(char_list)}) '
            print(f'{char_str:-^50}')

            url = f"https://www.prydwen.gg/star-rail/characters/{char}"
            data = fetch_character_data_with_selenium(url)

            save_result_to_file(data, f"data/{char}.pickle")
            print(f'Saved to file data/{char}.pickle (file size: {os.path.getsize(f"data/{char}.pickle") / 1024:.2f} KB)')

        except requests.ReadTimeout:
            print(f"Waiting time has expired for character {char}. Skip...")
            error_list.append(char)

        except Exception as e:
            print(f"Error for {char}: {e}")
            error_list.append(char)

        print('')
        time.sleep(5)

    if len(error_list) > 0:
        print(f'List of characters missed due to an error:{error_list}')
    else:
        print('All characters have been successfully processed.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing of character data.")
    parser.add_argument("-c", "--character", type=str, help="The name of the character to be parsed.")
    parser.add_argument("-a", "--all", action="store_true", help="Process all characters.")

    args = parser.parse_args()

    if args.all:
        char_list = fetch_character_links("https://www.prydwen.gg/star-rail/characters")[0]
        process_characters(char_list)

    elif args.character:
        try:
            process_characters([args.character])
        except Exception as e:
            print(f"Error during character processing '{args.character}': {e}")

    else:
        print("You must specify a character name or use the -a flag to process all characters.")
