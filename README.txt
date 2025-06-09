---

# Bestiary Arena Rankings Scraper Documentation

This Python script is designed to extract player profile data from Bestiary Arena, format it into a sortable wikitext table, and save it to a dynamically named file. It includes robust error handling, retry mechanisms for network issues, and comprehensive logging.

---

## Features

* **Player Data Extraction**: Fetches `exp`, `shell`, `tasks`, `playCount`, `ownedOutfits`, `perfectMonsters`, `bisEquips`, `rankPoints`, and `ticks` for each player.
* **Level Calculation**: Calculates player levels based on their experience points, with a base level of 1 for new players.
* **Wikitext Output**: Formats the extracted data into a Fandom-compatible sortable wikitext table.
* **Dynamic File Naming**: Generates an output filename that includes the UTC date and time (e.g., `Rankings (2024-01-23_143000_UTC).txt`).
* **Sorting**: Sorts all collected player data by **level in descending order** (highest level first). For players with the same level, it sorts them alphabetically by name.
* **Error Handling & Retries**: Implements a retry mechanism for failed API requests (up to 3 attempts) and logs all errors to a dedicated `error_log.txt` file.
* **Customizable Delays**: Allows configuration of delays between requests and retries to be polite to the API server.
* **Progress Indicators**: Prints progress messages to the console during data fetching.
* **Automatic Footer**: Adds an "Updated" timestamp (in UTC) and a Fandom category tag to the output file.

---

## Requirements

Before running the script, ensure you have Python installed (Python 3.6 or newer is recommended). You also need the `requests` library.

### Install Dependencies

Open your terminal or command prompt and run the following command:

```bash
pip install requests
```

---

## How to Use

1.  **Save the Script**:
    Save the entire provided Python code as a `.py` file (e.g., `bestiary_scraper.py`).

2.  **Prepare `names.txt`**:
    In the **same directory** where you saved your script, create a plain text file named `names.txt`.
    * Each line in this file should contain one Bestiary Arena username.
    * The script will process each name listed in this file.
    * **Example `names.txt`:**
        ```
        PlayerOne
        AnotherUser
        LegendaryPlayer
        NonExistentPlayer
        ```

3.  **Run the Script**:
    Open your terminal or command prompt, navigate to the directory where you saved your files, and execute the script:

    ```bash
    python bestiary_scraper.py
    ```

4.  **Monitor Output**:
    * The script will print messages to your console indicating its progress and any errors encountered.
    * Once finished, it will pause and prompt you to "Press Enter to exit...".

---

## Output Files

After running the script, you will find the following files in the same directory:

* **`Rankings (YYYY-MM-DD_HHMMSS_UTC).txt`**: This is your main output file. Its name will vary based on the date and time of execution (e.g., `Rankings (2024-01-23_143000_UTC).txt`). This file contains the collected player data formatted as a sortable wikitext table, ready to be pasted directly onto a Fandom wiki page.
* **`error_log.txt`**: If any errors occurred during the data fetching process (e.g., a player not found, API issues, or unexpected data), this file will be created or updated. It contains a timestamped log of all errors encountered, which is crucial for troubleshooting.

---

## Configuration

You can customize the script's behavior by modifying the following constants at the beginning of the `fetch_and_format_profile_data` function:

* **`MAX_RETRIES`**:
    * **Default**: `3`
    * The maximum number of times the script will attempt to re-fetch data for a single player if an error occurs.
* **`RETRY_DELAY`**:
    * **Default**: `0.5` (seconds)
    * The delay in seconds before retrying a failed request for a player.
* **`REQUEST_DELAY`**:
    * **Default**: `0.5` (seconds)
    * The delay in seconds between successful API requests for different players. This is important to avoid overwhelming the Bestiary Arena server and to reduce the risk of being rate-limited.

---

## Troubleshooting

If you encounter errors, check the following:

* **Exact Error Message**: Always look for the specific error message printed in your console or, more reliably, in the `error_log.txt` file. This message is key to diagnosing the problem.
* **`names.txt`**: Ensure `names.txt` exists in the same directory as the script and contains valid usernames, each on a new line.
* **`requests` Library**: Verify that the `requests` library is installed correctly (`pip install requests`).
* **Internet Connection**: Confirm your internet connection is active and stable.
* **Bestiary Arena API**: Check if `https://bestiaryarena.com` is online and accessible in your web browser. If the site or its API is down, the script won't be able to fetch data.
* **API Response Structure**: If the script logs errors about "Unexpected JSON structure," it might mean the Bestiary Arena API has changed its data format. In this case, the script would need to be updated to match the new structure.

---
