from text_utils import get_text_with_spaces

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

import requests
import time
import re


def parse_light_cones(soup: BeautifulSoup, char_element: str) -> pd.DataFrame:
    """
    Parse the "Best Light Cones" section of a character page into a DataFrame.

    Args:
        soup (bs4.BeautifulSoup): The parsed HTML of the character page.
        char_element (str): The character element to narrow down the search.

    Returns:
        pandas.DataFrame: A DataFrame with columns "name", "%", "rarity", "superimposition", and "description".
    """
    light_cones_data = []

    # Search for the "Best Light Cone" section by partial text
    light_cones_section = None
    for div in soup.find_all('div', class_=f'content-header {char_element}'):
        if 'Best Light Cones' in div.get_text():
            light_cones_section = div
            break

    if light_cones_section:
        print("✔ - Best Light Cones")

        parent_div = light_cones_section.find_next('div')
        detailed_cones = parent_div.find_all('div', class_='detailed-cones moc')

        if not detailed_cones:
            detailed_cones = parent_div.find_all('div', class_=f'single-cone with-notes {char_element}')
            
        for cone in detailed_cones:
            percentage_tag = cone.find('div', class_='percentage')
            percentage = percentage_tag.get_text(strip=True).replace('%', '') if percentage_tag else None

            name_tag = cone.find('span', class_='hsr-set-name')
            name = name_tag.get_text(strip=True) if name_tag else None
            rarity = name_tag.get('class', [])[1].split('-')[-1] if name_tag else None

            overlay_tag = cone.find('span', class_='cone-super')
            superimposition = overlay_tag.get_text(strip=True).replace('(', '').replace(')', '').replace('S', '') if overlay_tag else None

            description_tag = cone.find_next('div', class_=f'information {char_element}')
            description = description_tag.get_text(strip=True) if description_tag else None

            if not description:
                description_tag = cone.find_next_sibling('div', class_=f'information {char_element}')
                description = description_tag.get_text(strip=True) if description_tag else None

            light_cones_data.append({
                "name": name,
                "%": percentage,
                "rarity": rarity,
                "superimposition": superimposition,
                "description": description
            })

    else:
        print("✖ - Best Light Cones")

    return pd.DataFrame(light_cones_data)


def parse_relics(soup: BeautifulSoup, char_element: str) -> pd.DataFrame:
    """
    Parse the Best Relics section of the webpage into a DataFrame.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML of the webpage.
    char_element : str
        The character element to narrow down the search.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the following columns:

        * name: The name of the relic set.
        * %: The percentage of effectiveness of a set of relics for a character.
        * 2 piece: The 2-piece set bonus.
        * 4 piece: The 4-piece set bonus.
        * flex: A boolean indicating whether the relic set has a flex placeholder.
        * info: The information text associated with the relic set, if it has notes.

    """
    relics_data = []

    # Parse Best Relics
    build_relics_section = soup.find('h6', string='Best Relic Sets')

    if build_relics_section:
        print("✔ - Best Relic Sets Found")

        # Find all relic containers
        relics_containers = build_relics_section.find_next_siblings('div', class_='detailed-cones moc extra planar')

        if relics_containers:
            print("✔ - Best Relic Sets / Relics Containers")
        else:
            print("✖ - Best Relics / Relics Container")
        
        for relics_container in relics_containers:
            # Obtaining a list of all relics and information
            relic_elements = relics_container.find_all('div', class_=[f'single-cone with-notes {char_element}', f'single-cone {char_element}'])
            info_elements = relics_container.find_all('div', class_=f'information {char_element}')

            info_iter = iter(info_elements)

            # Relic processing inside the container to "Best Planetary Sets"
            for relic in relic_elements:
                if relic.find_previous('h6', string='Best Planetary Sets'):
                    break

                # Checking the availability of "flex-placeholder" for each relic with "with-notes"
                flex_placeholder = None
                if relic.get('class') and 'with-notes' in relic.get('class'):
                    flex_placeholder = relic.find('div', class_='flex-placeholder')
                flex_value = 1 if flex_placeholder else 0

                # Percentage extraction
                percentage_tag = relic.find('div', class_='percentage')
                percentage = get_text_with_spaces(percentage_tag.find('p')) if percentage_tag else None

                # Name extraction
                name_tag = relic.find('button')
                name = get_text_with_spaces(name_tag).split('\n')[-1] if name_tag else None

                # Extracting descriptions (2 piece and 4 piece)
                description_2, description_4 = "", ""
                accordion_item = relic.find('div', class_='accordion-item')
                if accordion_item:
                    description_sections = accordion_item.find_all('div', class_='hsr-set-description')
                    for desc in description_sections:
                        for part in desc.find_all('div'):
                            set_piece = part.find('span', class_='set-piece')
                            text = part.find('p')
                            if set_piece and text:
                                if set_piece.get_text(strip=True) == "(2)":
                                    description_2 = get_text_with_spaces(text)
                                elif set_piece.get_text(strip=True) == "(4)":
                                    description_4 = get_text_with_spaces(text)

                # Extract from “with-notes” class
                information_text = ""
                if relic.get('class') and 'with-notes' in relic.get('class'):
                    information_div = next(info_iter, None)
                    if information_div:
                        information_text = get_text_with_spaces(information_div)

                relics_data.append({
                    "name": name,
                    "%": percentage,
                    "2 piece": description_2,
                    "4 piece": description_4,
                    "flex": flex_value,
                    "info": information_text
                })
    
    else:
        print("✖ - Best Relics")

    relics_df = pd.DataFrame(relics_data)

    return relics_df


def parse_planar_sets(soup: BeautifulSoup, char_element: str) -> pd.DataFrame:
    """
    Parse the Best Planetary Sets and Special Planetary Sets sections of the webpage into DataFrames.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML of the webpage.
    char_element : str
        The character element to narrow down the search.

    Returns
    -------
    pd.DataFrame, dict
        A tuple containing two elements:

        1. A DataFrame with the following columns:

            * Name: The name of the planetary set.
            * %: The percentage of effectiveness of a planetary set for a character.
            * 2 piece: The 2-piece set bonus.
            * info: The information text associated with the planetary set, if it has notes.

        2. A dictionary containing additional information extracted from the sections, with the following keys:

            * p: The text of the <p> element following the Best Planetary Sets section.
            * ul: The text of the <ul> element following the Best Planetary Sets section.

    """
    
    def extract_planar_sets(section_header: str) -> tuple[list, dict]:
        """
        Extracts planar sets data from the given section header.

        Args:
            section_header (str): The header string of the section to extract.

        Returns:
            list: A list of dictionaries containing the extracted data.
            dict: A dictionary containing additional information extracted from the section.
        """
        planar_sets_data = []
        additional_info = {"p": None, "ul": None}

        section = soup.find('h6', string=section_header)
        if section:
            print(f"✔ - {section_header}")

            container = section.find_next_sibling('div', class_='detailed-cones moc extra planar')

            if not container:
                container = section.find_next('div', class_='detailed-cones moc extra planar')

            if container:
                print(f"✔ - {section_header} / Planar Sets Container")

                elements = container.find_all(['div'])
                i = 0
                while i < len(elements):
                    element = elements[i]

                    if 'single-cone' in element.get('class', []):
                        # Percentage
                        percentage_tag = element.find('div', class_='percentage')
                        percentage = get_text_with_spaces(percentage_tag.find('p')) if percentage_tag else None

                        # Name
                        name_tag = element.find('button')
                        name = get_text_with_spaces(name_tag).split('\n')[-1] if name_tag else None

                        # Desctiption
                        description_tag = element.find('div', class_='hsr-set-description')
                        description = ""
                        if description_tag:
                            description_parts = description_tag.find_all('div')
                            for part in description_parts:
                                set_piece = part.find('span', class_='set-piece')
                                text = part.find('p')
                                if set_piece and text and set_piece.get_text(strip=True) == "(2)":
                                    description = get_text_with_spaces(text)

                        # Extract from “with-notes” class
                        information = None
                        if 'with-notes' in element.get('class', []):
                            next_information = element.find_next_sibling('div', class_='information')
                            if next_information and char_element in next_information.get('class', []):
                                information = get_text_with_spaces(next_information)

                        planar_sets_data.append({
                            "name": name,
                            "%": percentage,
                            "2 piece": description,
                            "info": information
                        })

                    i += 1

                # Extraction of additional information (<p> and <ul>)
                additional_p = container.find('p', class_='with-margin-top')
                additional_ul = container.find('ul', class_='with-sets')
                additional_info["p"] = get_text_with_spaces(additional_p)
                additional_info["ul"] = get_text_with_spaces(additional_ul)

            else:
                print(f"✖ - {section_header} / Planar Sets Container")

        else:
            print(f"✖ - {section_header} (or section not found)")

        return planar_sets_data, additional_info

    # Extract data for both sections
    best_planar_sets, best_additional_info = extract_planar_sets("Best Planetary Sets")
    special_planar_sets, _ = extract_planar_sets("Special Planetary Sets")

    # Combine data from both sections
    all_planar_sets_data = best_planar_sets + special_planar_sets

    planar_sets_df = pd.DataFrame(all_planar_sets_data)

    return planar_sets_df, best_additional_info


def characteristics_to_df(data: list[str]) -> pd.DataFrame:
    """
    Parse a list of strings in the format 'Characteristic: value' into a DataFrame.

    Parameters
    ----------
    data : list of str
        A list of strings, where each string is in the format 'Characteristic: value'.
        The value can be a range (e.g. '1-2'), a single value with a comment (e.g. '3 (foo)'),
        or a single value with a plus sign (e.g. '4+').

    Returns
    -------
    df : pd.DataFrame
        A DataFrame with the following columns:

        * characteristic: The name of the characteristic (e.g. 'ATK')
        * min: The minimum value of the characteristic (e.g. 1)
        * max: The maximum value of the characteristic (e.g. 2)
        * plus: A boolean indicating whether the value has a plus sign (e.g. True)
        * fix1, fix2, fix3: The fixed values of the characteristic (e.g. 3, 4, 5)
        * min comment, max comment,fix1 comment, fix2 comment, fix3 comment: The comments associated with the values
        * text: The text value of the characteristic (e.g. 'foo')
        * raw: The original string (e.g. 'Characteristic: 1-2 (foo)')

    """

    # Initialize lists to store extracted data
    characteristics = []
    mins = []
    maxs = []
    plus_flags = []
    fix1s = []
    fix2s = []
    fix3s = []
    min_comments = []
    max_comments = []
    fix1_comments = []
    fix2_comments = []
    fix3_comments = []
    texts = []
    raws = []

    for item in data:
        raw = item
        parts = item.split(":", 1)

        if len(parts) == 2:
            char_name, value = parts
        else:
            char_name = parts[0]
            value = ""

        # Remove excess spaces
        char_name = char_name.strip()
        value = value.strip()
        
        # Default placeholders
        min_val, max_val, fix1, fix2, fix3 = None, None, None, None, None
        min_comment, max_comment, fix1_comment, fix2_comment, fix3_comment = None, None, None, None, None
        plus_flag, text = False, None

        # Default placeholders
        min_val, max_val, fix1, fix2, fix3 = None, None, None, None, None
        min_comment, max_comment, fix1_comment, fix2_comment, fix3_comment = None, None, None, None, None
        plus_flag, text = False, None

        try:
            # Specific case handling
            if "1-2 Speed slower than carry" in value:
                match = re.match(r"(1-2 Speed slower than carry)(.*?)\s*/\s*(\d+\+?)\s*(\(.*\))?", value)
                if match:
                    text = match.group(1)
                    min_val = match.group(3)
                    if min_val.endswith("+"):
                        plus_flag = True
                        min_val = min_val[:-1]
                    if match.group(4):
                        min_comment = match.group(4)
            elif "1-2 Speed slower than the carry" in value:
                match = re.match(r"(1-2 Speed slower than the carry.*?)(,\s*)(\d+\+?)\s*(.*)", value)
                if match:
                    text = match.group(1)
                    min_val = match.group(3)
                    if min_val.endswith("+"):
                        plus_flag = True
                        min_val = min_val[:-1]
                    min_comment = match.group(4)
            elif "Base Speed" in value:
                match = re.match(r"(Base Speed.*?/\s*)(\d+)", value)
                if match:
                    fix1 = match.group(1).strip()
                    fix2 = match.group(2)
            elif re.match(r"(\d+\+?)\s*(\(.*?\))\s*/\s*(\d+\+?)\s*(\(.*\))", value):
                match = re.match(r"(\d+\+?)\s*(\(.*?\))\s*/\s*(\d+\+?)\s*(\(.*\))", value)
                if match:
                    fix1 = match.group(1)
                    fix1_comment = match.group(2)
                    fix2 = match.group(3)
                    fix2_comment = match.group(4)
            else:
                # Default handling for ranges and fixed values
                if "/" in value:
                    fixed_parts = [part.strip() for part in value.split("/")]
                    fix1 = fixed_parts[0] if len(fixed_parts) > 0 else None
                    fix2 = fixed_parts[1] if len(fixed_parts) > 1 else None
                    fix3 = fixed_parts[2] if len(fixed_parts) > 2 else None

                    # Extract comments if present
                    if fix3 and "(" in fix3:
                        fix3, fix3_comment = re.match(r"(.*?)(\(.*\))", fix3).groups()
                        fix3 = fix3.strip()
                    elif fix2 and "(" in fix2:
                        fix2, fix2_comment = re.match(r"(.*?)(\(.*\))", fix2).groups()
                        fix2 = fix2.strip()
                    elif fix1 and "(" in fix1:
                        fix1, fix1_comment = re.match(r"(.*?)(\(.*\))", fix1).groups()
                        fix1 = fix1.strip()
                else:
                    range_with_comment = re.match(r"(\d+\.?\d*%?)\s*(\(.*?\))?\s*-\s*(\d+\.?\d*%?)\+?\s*(\(.*?\))?", value)
                    single_value_with_comment = re.match(r"(\d+\.?\d*%?)\+?\s*(\(.*\))?", value)

                    if range_with_comment:
                        min_val = range_with_comment.group(1)
                        if range_with_comment.group(2):
                            min_comment = range_with_comment.group(2)
                        max_val = range_with_comment.group(3)
                        if range_with_comment.group(4):
                            max_comment = range_with_comment.group(4)
                        plus_flag = "+" in value

                    elif single_value_with_comment:
                        min_val = single_value_with_comment.group(1)
                        if single_value_with_comment.group(2):
                            min_comment = single_value_with_comment.group(2)
                        plus_flag = "+" in value
                    else:
                        text = value

        except Exception as e:
            print(f"Error processing value '{value}': {e}")

        # Append to lists
        characteristics.append(char_name)
        mins.append(min_val)
        maxs.append(max_val)
        plus_flags.append(plus_flag)
        fix1s.append(fix1)
        fix2s.append(fix2)
        fix3s.append(fix3)
        min_comments.append(min_comment)
        max_comments.append(max_comment)
        fix1_comments.append(fix1_comment)
        fix2_comments.append(fix2_comment)
        fix3_comments.append(fix3_comment)
        texts.append(text)
        raws.append(raw)

    # Create DataFrame
    df = pd.DataFrame({
        'characteristic': characteristics,
        'min': mins,
        'max': maxs,
        'plus': plus_flags,
        'fix1': fix1s,
        'fix2': fix2s,
        'fix3': fix3s,
        'min comment': min_comments,
        'max comment': max_comments,
        'fix1 comment': fix1_comments,
        'fix2 comment': fix2_comments,
        'fix3 comment': fix3_comments,
        'text': texts,
        'raw': raws
    })

    return df


def parse_stats(soup: BeautifulSoup, char_element: str) -> tuple[pd.DataFrame, dict, dict, str, str, str, pd.DataFrame]:
    """
    Parse the Best Stats section of the webpage into a DataFrame.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML of the webpage.
    char_element : str
        The character element to narrow down the search.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the following columns:

        * Part: The name of the part (e.g. 'Flower of Life', 'Plume of Death', etc.).
        * Stats: A string containing the names of the stats of the part, separated by commas.

    dict
        A dictionary where the keys are the part names and the values are another dictionary.
        The inner dictionary has the stat names as keys and the importance level (0-4) as values.

    dict
        A dictionary containing the substats information. The keys are the priorities (0-4) and the values are lists of stat names.

    str
        The substats text.

    str
        The details info text.

    str
        The comments text.

    pandas.DataFrame
        A DataFrame with the recommended endgame stats.
    """
    
    stats_data = []
    stats_dict = {}
    substats_dict = {}

    # Search for “Best Stats” section
    best_stats_section = soup.find('div', class_='build-stats')
    if best_stats_section:
        print("✔ - Best Stats")

        main_stats_section = best_stats_section.find('div', class_='main-stats')

        if main_stats_section:
            print("✔ - Best Stats / Main Stats")

            for col in main_stats_section.find_all('div', class_='col'):
                part_name_tag = col.find('div', class_='stats-header span') or col.find('div', class_='stats-header')
                part_name = get_text_with_spaces(part_name_tag)

                list_stats = col.find('div', class_='list-stats')
                if list_stats:
                    stats = []
                    importance_dict = {}

                    for i, stat_block in enumerate(list_stats.find_all('div', class_='hsr-stat')):
                        stat_name = get_text_with_spaces(stat_block.find('span'))
                        stats.append(stat_name)

                        if i not in importance_dict:
                            importance_dict[i] = []
                        importance_dict[i].append(stat_name)

                    stats_data.append({
                        "Part": part_name,
                        "Stats": ', '.join(stats)
                    })

                    stats_dict[part_name] = importance_dict

        else:
            print("✖ - Best Stats / Main Stats")

        # Parsing “Substats”
        substats_section = best_stats_section.find('div', class_='sub-stats')
        substats_text = get_text_with_spaces(substats_section) if substats_section else ""

        if substats_text:
            substats_parts = substats_text.split('>')
            for priority, part in enumerate(substats_parts):
                equal_stats = [stat.strip() for stat in part.split('=')]
                substats_dict[priority] = equal_stats

        # Parsing additional information about stats
        details_info_button = best_stats_section.find('button', string='Details about the Stats')
        details_info = ""
        if details_info_button:
            details_info_section = details_info_button.find_next('div', class_='accordion-body')
            details_info = get_text_with_spaces(details_info_section)

        # Parsing Comments
        comments_section = best_stats_section.find('div', class_='stats-comments')
        comments_text = get_text_with_spaces(comments_section.find('p')) if comments_section else ""
        
        # Parsing Recommended endgame stats
        endgame_header = None
        for div in best_stats_section.find_all('div', class_=f'content-header {char_element}'):
            if 'Recommended endgame stats' in div.get_text():
                endgame_header = div
                break

        endgame_data = []
        if endgame_header:
            endgame_list = endgame_header.find_next_sibling('div')
            if endgame_list:
                raw_list = endgame_list.find('div', class_='raw list')

                raw_list_ul = None
                if raw_list:
                    raw_list_ul = raw_list.find('ul', recursive=False)

                if raw_list_ul:
                    for item in raw_list_ul.find_all('li', recursive=False):
                        # Getting text of the element
                        stat_text = get_text_with_spaces(item.find('p'))

                        # Check for nested lists
                        nested_list = item.find('ul')
                        if nested_list:
                            # Add text of nested elements to the main element
                            nested_text = " ".join(
                                get_text_with_spaces(nested_item.find('p'))
                                for nested_item in nested_list.find_all('li')
                            )
                            stat_text += f" {nested_text}"
                        
                        endgame_data.append(stat_text)

        endgame_df = characteristics_to_df(endgame_data)

        # Converting data into a “DataFrame”
        stats_df = pd.DataFrame(stats_data)

        return stats_df, stats_dict, substats_dict, substats_text, details_info, comments_text, endgame_df

    print("✖ - Best Stats")
    return pd.DataFrame(), {}, {}, "", "", "", pd.DataFrame()


def parse_traces_priority(soup: BeautifulSoup, char_element: str) -> dict:
    """
    Parse the "Traces priority" section of a character page into a dictionary.

    Args:
        soup (bs4.BeautifulSoup): The parsed HTML of the character page.
        char_element (str): The character element to narrow down the search.

    Returns:
        dict: A dictionary with two keys: "Skills priority" and "Major Traces priority".
    """
    traces_dict = {}

    # Search for “Traces priority” section
    traces_section = None
    for div in soup.find_all('div', class_=f'content-header {char_element}'):
        if 'Traces priority' in div.get_text():
            traces_section = div
            break

    if traces_section:
        print("✔ - Traces priority")
        # Parsing "Skills priority"
        skills_priority_section = traces_section.find_next('div', class_='row')
        if skills_priority_section:
            skills_box = skills_priority_section.find('div', class_='box sub-stats')
            if skills_box:
                skills_text = get_text_with_spaces(skills_box.find('p'))
                if skills_text:
                    skills_parts = skills_text.split('>')
                    skills_priority = {}
                    for priority, part in enumerate(skills_parts):
                        equal_skills = [skill.strip() for skill in part.split('=')]
                        skills_priority[priority] = equal_skills
                    traces_dict['Skills priority'] = skills_priority

        # Parsing "Major Traces priority"
        major_traces_section = skills_priority_section.find_next('div', class_='row')
        if major_traces_section:
            major_traces_box = major_traces_section.find('div', class_='box sub-stats')
            if major_traces_box:
                major_traces_text = get_text_with_spaces(major_traces_box.find('p'))
                if major_traces_text:
                    major_traces_parts = major_traces_text.split('>')
                    major_traces_priority = {}
                    for priority, part in enumerate(major_traces_parts):
                        major_traces_priority[priority] = part.strip()
                    traces_dict['Major Traces priority'] = major_traces_priority
    
    else:
        print("✖ - Traces priority")

    return traces_dict


def parse_synergy(soup: BeautifulSoup, char_element: str) -> list[str]:
    """
    Parse the "Synergy" section of a character page into a list of strings.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML content of the character page.
    char_element : str
        The character element to narrow down the search.

    Returns
    -------
    list of str
        A list of strings, each containing the name of a character in the synergy list.
    """

    characters = []

    # Searching for “Synergy” section
    synergy_section = None
    for div in soup.find_all('div', class_=f'content-header {char_element}'):
        if 'Synergy' in div.get_text():
            synergy_section = div
            break

    if synergy_section:
        print("✔ - Synergy")
        # Find "ul" with class “bigger-margin”
        synergy_list = synergy_section.find_next_sibling('ul', class_='bigger-margin')
        if synergy_list:
            for item in synergy_list.find_all('li'):
                # Find all the characters inside “li”
                for character_tag in item.find_all('span', class_='inline-name'):
                    character_name = get_text_with_spaces(character_tag)
                    characters.append(character_name)

    else:
        print("✖ - Synergy")

    return characters


def parse_teams(soup: BeautifulSoup) -> list[dict]:
    """
    Parse the "Teams (MoC)" section of a character page to extract team data.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML content of the character page.

    Returns
    -------
    list of dict
        A list of dictionaries, each containing the following keys:
        - 'rank': int or None, the rank of the team.
        - 'usage': float or None, the usage percentage of the team.
        - 'rounds': float or None, the average number of rounds for the team.
        - 'team': list of str, the names of characters in the team.
    """

    teams_data = []

    # Find the “commands” container
    container = soup.find('div', class_='team-container-moc')
    if not container:
        print("✖ - Teams (MoC)")   
        return teams_data

    print("✔ - Teams (MoC)")

    # Find the command lines
    team_rows = container.find_all('div', class_='team-row')
    for row in team_rows:
        # Rank extraction
        rank_tag = row.find('p', class_='rank')
        rank = int(rank_tag.get_text(strip=True).replace('Rank', '').strip()) if rank_tag else None

        # Usage extraction
        usage_tag = row.find('p', class_='usage')
        usage = float(usage_tag.get_text(strip=True).replace('App. rate:', '').replace('%', '').strip()) if usage_tag else None

        # Rounds extraction
        rounds_tag = row.find('p', class_='rounds')
        rounds = float(rounds_tag.get_text(strip=True).replace('Avg. cycles:', '').strip()) if rounds_tag else None

        # Extraction team (characters)
        team_characters = []
        character_tags = row.find_all('a', href=True)
        for char_tag in character_tags:
            character_name = char_tag['href'].split('/')[-1]  # Extracting a name from a link
            team_characters.append(character_name.capitalize())

        # Add team data to the list
        teams_data.append({
            'rank': rank,
            'usage': usage,
            'rounds': rounds,
            'team': team_characters
        })

    return teams_data


def find_element_from_page(soup: BeautifulSoup) -> str | None:
    """
    Finds and returns the most frequent element class from a predefined list within the provided HTML page.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The parsed HTML content of the webpage.

    Returns
    -------
    str or None
        The element class with the highest occurrence if found; otherwise, None. 
        Prints a warning if multiple elements are found.
    """

    # List of elements to search for
    elements_to_find = ["Physical", "Lightning", "Fire", "Imaginary", "Ice", "Wind", "Quantum"]

    try:
        # Find each element on the page and count their number
        element_counts = {element: len(soup.find_all(class_=element)) for element in elements_to_find}

        # Leave only the elements that are on the page
        found_elements = {element: count for element, count in element_counts.items() if count > 0}

        # Checking the results
        if len(found_elements) == 1:
            return max(found_elements, key=found_elements.get)
        elif len(found_elements) >= 2:
            print(f"Warning, found {len(found_elements)} elements: {found_elements}")
            return max(found_elements, key=found_elements.get)
        else:
            print("Element not found on the page.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error when loading the page: {e}")
        return None


def fetch_character_data_with_selenium(url: str) -> dict:
    """
    Fetches data from a Star Rail character page using Selenium.

    Args:
        url (str): URL of the character page.

    Returns:
        dict: A dictionary containing the following keys:

            * light cones: A DataFrame containing the data for the light cones.
            * relics: A DataFrame containing the data for the relics.
            * planar sets: A DataFrame containing the data for the planar sets.
            * additional planar sets: A dictionary containing the data of additional planar sets.
            * relic main stats: A DataFrame containing the data for the relic main stats.
            * relic main stats dict: A dictionary containing the relic main stats with importance levels.
            * substats: A string containing the substats.
            * substats dict: A dictionary containing the substats with importance levels.
            * substats details: A string containing the substats details.
            * substats comments: A string containing the substats comments.
            * endgame stats: A DataFrame containing the data for the endgame stats.
            * traces priority: A dictionary containing the traces priority.
            * synergy: A list of synergy characters.
            * teams (MoC): A list of teams with rank, usage%, and rounds.
            * element: The element of the character.

    Note:
        Requires Selenium and a Chrome driver to be installed.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # without opening a browser window
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 10)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        char_element = find_element_from_page(soup)

        # Waiting for all buttons “single-tab char_element”
        tabs = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, f"single-tab.{char_element}"))
        )

        # Selecting the desired button by text
        build_and_teams_tab = None
        for tab in tabs:
            if "Build and teams" in tab.text:
                build_and_teams_tab = tab
                break

        if build_and_teams_tab is None:
            raise Exception("Кнопка 'Build and teams' не найдена.")

        # Scroll slightly above the button so the “header” doesn't overlap
        driver.execute_script("arguments[0].scrollIntoView(true);", build_and_teams_tab)
        driver.execute_script("window.scrollBy({top: -100, left: 0, behavior: 'smooth'});")
        time.sleep(1)  # Ждём прокрутки

        # If the element is overlapped, we use JavaScript to click it
        try:
            build_and_teams_tab.click()
        except:
            driver.execute_script("arguments[0].click();", build_and_teams_tab)

        time.sleep(2)  # Waiting for the content to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        light_cones_df = parse_light_cones(soup, char_element)
        relics_df = parse_relics(soup, char_element)
        planar_sets_df, additional_planar_sets = parse_planar_sets(soup, char_element)
        stats_df, stats_dict, substats_dict, substats, details_info, comments, endgame_df = parse_stats(soup, char_element)
        traces_dict = parse_traces_priority(soup, char_element)
        synergy_characters = parse_synergy(soup, char_element)
        teams_data = parse_teams(soup)

        # Combine all results into a dictionary
        result = {
            "light cones": light_cones_df,
            "relics": relics_df,
            "planar sets": planar_sets_df,
            "additional planar sets": additional_planar_sets,
            "relic main stats": stats_df,
            "relic main stats dict": stats_dict,
            "substats": substats,
            "substats dict": substats_dict,
            "substats details": details_info,
            "substats comments": comments,
            "endgame stats": endgame_df,
            "traces priority": traces_dict,
            "synergy": synergy_characters,
            "teams (MoC)": teams_data,
            "element": char_element,
        }

        return result

    finally:
        driver.quit()

