import requests
import math
import time
import json
import datetime
from datetime import timezone

def fetch_and_format_profile_data(names_file, output_file, error_log_file):
    """
    Fetches profile data for names from a file, collects it, sorts by level descending,
    and then writes it to another file in wikitext format, with retry logic and an error log.
    Includes wikitext header and footer with UTC timestamp.
    """
    MAX_RETRIES = 3    # Maximum number of retries for each name
    RETRY_DELAY = 0.4  # Delay in seconds between retries
    REQUEST_DELAY = 0.4 # Delay in seconds between successful requests
    
    error_log_messages = [] 
    all_profile_data = []   

    def log_error(message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        print(f"ERROR: {message}") 
        error_log_messages.append(full_message)

    try:
        with open(names_file, 'r') as file:
            names = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        log_error(f"The names file '{names_file}' was not found. Please ensure it exists.")
        return

    if not names:
        print("No names found in the names file. Exiting.")
        return

    print(f"Processing {len(names)} names...")
    for i, name in enumerate(names):
        print(f"Fetching data for '{name}' ({i+1}/{len(names)})...")
        retries = 0
        success = False
        profile_entry = None 

        while retries < MAX_RETRIES and not success:
            url = f"https://bestiaryarena.com/api/trpc/serverSide.profilePageData?batch=1&input=%7B%220%22:%7B%22json%22:%22{name}%22%7D%7D"
            
            try:
                response = requests.get(url, timeout=10) 
                response.raise_for_status() 

                data = response.json()
                profile_data_raw = data[0]["result"]["data"]["json"]
                
                exp = profile_data_raw.get("exp", 0)
                shell = profile_data_raw.get("shell", "N/A")
                tasks = profile_data_raw.get("tasks", "N/A")
                play_count = profile_data_raw.get("playCount", 0)
                owned_outfits = profile_data_raw.get("ownedOutfits", "N/A")
                perfect_monsters = profile_data_raw.get("perfectMonsters", "N/A")
                bis_equips = profile_data_raw.get("bisEquips", "N/A")
                rank_points = profile_data_raw.get("rankPoints", 0)
                ticks = profile_data_raw.get("ticks", 0)

                level = math.floor(exp / 400) + 1 if exp is not None else 1 

                profile_entry = {
                    "name": name,
                    "level": level,
                    "play_count": play_count,
                    "rank_points": rank_points,
                    "ticks": ticks,
                    "shell": shell,
                    "tasks": tasks,
                    "perfect_monsters": perfect_monsters,
                    "bis_equips": bis_equips,
                    "owned_outfits": owned_outfits,
                    "exp": exp
                }
                all_profile_data.append(profile_entry)
                success = True 

            except requests.exceptions.RequestException as e:
                log_error(f"Attempt {retries + 1}/{MAX_RETRIES}: Network/HTTP error for '{name}': {e}")
            except json.JSONDecodeError:
                log_error(f"Attempt {retries + 1}/{MAX_RETRIES}: Failed to parse JSON for '{name}'. Response content (first 200 chars): {response.text[:200]}...")
            except (KeyError, IndexError):
                log_error(f"Attempt {retries + 1}/{MAX_RETRIES}: Unexpected JSON structure for '{name}'. Response content (first 200 chars): {response.text[:200]}...")
            
            if not success:
                retries += 1
                if retries < MAX_RETRIES:
                    print(f"Retrying for '{name}' in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY) 
                else:
                    log_error(f"All {MAX_RETRIES} attempts failed for '{name}'. Skipping this name.")
                    continue 
        
        if success:
            time.sleep(REQUEST_DELAY) 

    print("\nFinished fetching data for all names. Sorting and writing to file...")

    all_profile_data.sort(key=lambda x: (x['level'], x['name'].lower()), reverse=True)

    with open(output_file, 'w') as output_file_handle:
        output_file_handle.write("This table presents current rankings for all characters who have completed all 53 [[:Category:Maps|maps]], sorted by levels. See documentation [https://github.com/styrserver/BestiaryArenaRankings here].\n")
        output_file_handle.write("{| class=\"sortable fandom-table\"\n")
        output_file_handle.write("!'''Username'''\n")
        output_file_handle.write("!'''Level'''\n")
        output_file_handle.write("!<abbr title=\"Successful runs\">[[File:Match-count.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Rank Points\">[[File:Grade.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Time Sum\">[[File:Speed.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Daily Seashell\">[[File:Shell-count.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Hunting tasks\">[[File:Task-count.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Perfect Creatures\">[[File:Enemy.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"BIS Equipment\">[[File:Equips.png|frameless]]</abbr>\n")
        output_file_handle.write("!<abbr title=\"Bag Outfits\">[[File:Mini-outfitbag.png|frameless]]</abbr>\n")
        output_file_handle.write("|-\n")

        for entry in all_profile_data:
            output_file_handle.write(f"|[https://bestiaryarena.com/profile/{entry['name']} {entry['name']}]\n")
            output_file_handle.write(f"|{entry['level']}\n")
            output_file_handle.write(f"|{entry['play_count']}\n")
            output_file_handle.write(f"|{entry['rank_points']}\n")
            output_file_handle.write(f"|{entry['ticks']}\n")
            output_file_handle.write(f"|{entry['shell']}\n")
            output_file_handle.write(f"|{entry['tasks']}\n")
            output_file_handle.write(f"|{entry['perfect_monsters']}\n")
            output_file_handle.write(f"|{entry['bis_equips']}\n")
            output_file_handle.write(f"|{entry['owned_outfits']}\n")
            output_file_handle.write(f"|-\n")

        current_utc_time = datetime.datetime.now(timezone.utc)
        current_utc_time_str = current_utc_time.strftime("%Y-%m-%d %H:%M:%S UTC%z").replace("UTC+0000", "UTC+0")

        output_file_handle.write(f"|}}\n")
        output_file_handle.write(f"''<small>Updated ({current_utc_time_str}).</small>''\n")
        output_file_handle.write("[[Category:Highscores]]\n")

    print(f"\nData has been written to {output_file}")

if __name__ == "__main__":
    names_file_path = 'Bestplayers.txt'
    error_log_file_path = 'error_log.txt' 

    current_utc_time_for_filename = datetime.datetime.now(timezone.utc)
    filename_timestamp = current_utc_time_for_filename.strftime("%Y-%m-%d_%H%M%S_UTC")
    output_file_path = f"Rankings ({filename_timestamp}).txt"

    print("Starting data extraction script...")
    fetch_and_format_profile_data(names_file_path, output_file_path, error_log_file_path)

    input("\nScript finished. Press Enter to exit...")
