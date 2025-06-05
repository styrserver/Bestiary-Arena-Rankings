import requests
import time
import json

# --- Configuration ---
BASE_URL = "https://bestiaryarena.com/api/trpc/serverSide.profilePageData?batch=1&input="
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0.5
REQUEST_DELAY_SECONDS = 0.1
TIMEOUT_SECONDS = 10

# --- Data Storage ---
failed_users_profile_none = set()  # Use a set to prevent duplicates

# --- Helper Functions ---
def build_profile_url(username: str) -> str:
    """Constructs the API URL for a given username."""
    input_param = {"0": {"json": username}}
    encoded_input = requests.utils.quote(json.dumps(input_param))
    return f"{BASE_URL}{encoded_input}"

def make_request(url: str) -> dict | None:
    """Makes an HTTP GET request with retries and a timeout."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY_SECONDS)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
    print(f"Failed to retrieve data after {MAX_RETRIES} attempts for {url}.")
    return None

def load_usernames(filename: str) -> set:
    """Loads usernames from a file, returning a set to eliminate duplicates."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return {line.strip() for line in file if line.strip()}
    except FileNotFoundError:
        print(f"Warning: {filename} not found.")
        return set()

def write_usernames(filename: str, usernames: set, mode='w'):
    """Writes unique usernames to a file."""
    try:
        with open(filename, mode, encoding='utf-8') as file:
            for user in sorted(usernames):  # Sort for consistency
                file.write(f"{user}\n")
        print(f"Successfully saved {len(usernames)} unique users to {filename}.")
    except IOError as e:
        print(f"Error writing to {filename}: {e}")

def process_user_profile(username: str) -> str | None:
    """Fetches and processes profile data for a single user."""
    print(f"Processing: {username}")
    url = build_profile_url(username)
    data = make_request(url)

    if not data:
        print(f"  No data retrieved for {username}. Keeping in DiscordNames.txt.")
        return None

    try:
        profile_data = data[0].get("result", {}).get("data", {}).get("json")

        if profile_data is None:
            print(f"  Profile data for {username} is None. Adding to failed_users.")
            failed_users_profile_none.add(username)  # Store in a set to avoid duplicates
            return None

        maps_completed = profile_data.get("maps", 0)

        if maps_completed < 53:
            print(f"  Skipping {username}: Maps completed ({maps_completed}) is below 53.")
            return None

        print(f"  Qualified: {username} (Maps: {maps_completed})")
        return username

    except (IndexError, KeyError, TypeError) as e:
        print(f"  Error parsing data for {username}: {e}. Keeping in DiscordNames.txt.")
        return None

def run_script():
    """Main function to run the data processing script."""
    failed_users = load_usernames('FailedUsers.txt')
    all_usernames = load_usernames('DiscordNames.txt')

    print("\033[92mFailedUsers have been read.\033[0m")  # Green message

    usernames_to_process = all_usernames - failed_users

    if not usernames_to_process:
        print("No users to process—all are previously failed.")
        return

    qualified_usernames = set()  # Use set to prevent duplicates
    for user in usernames_to_process:
        processed_user = process_user_profile(user)
        if processed_user:
            qualified_usernames.add(processed_user)  # Store in set to remove duplicates

    write_usernames("Bestplayers.txt", qualified_usernames)

    if failed_users_profile_none:
        print(f"\n--- Handling Failed Users (profile_data was None) ---")
        print(f"Users with 'None' profile data: {len(failed_users_profile_none)} usernames: {failed_users_profile_none}")

        updated_discord_usernames = all_usernames - failed_users_profile_none
        write_usernames('DiscordNames.txt', updated_discord_usernames)
        write_usernames('FailedUsers.txt', failed_users_profile_none, mode='a')

    print("\nScript execution finished.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        run_script()
    except Exception as e:
        print(f"Unexpected error: {e}")
        input("Press Enter to exit...")
