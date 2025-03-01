import requests
import json
import os
from dotenv import load_dotenv  # <-- Import dotenv

# Load environment variables from .env file
load_dotenv()

# Get Habitica credentials from environment variables
HABITICA_USER_ID = os.getenv("HABITICA_USER_ID")
HABITICA_API_TOKEN = os.getenv("HABITICA_API_TOKEN")
HABITICA_API_URL = "https://habitica.com/api/v3/tasks/user"

# URL to fetch Habitica tasks from GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/djamp1990/habitica-automation/main/habitica_tasks.json"

# API headers
HEADERS = {
    "x-api-user": HABITICA_USER_ID,
    "x-api-key": HABITICA_API_TOKEN,
    "Content-Type": "application/json"
}

# Fetch tasks from GitHub
def fetch_github_tasks():
    response = requests.get(GITHUB_RAW_URL)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch tasks from GitHub: {response.status_code}")
        return []
    
    try:
        tasks = response.json()
        
        # Ensure tasks are a list
        if not isinstance(tasks, list):
            print("❌ JSON structure error: Expected a list of tasks")
            return []
        
        return tasks
    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error: {e}")
        return []

# Check for existing tasks in Habitica
def get_existing_tasks():
    response = requests.get(HABITICA_API_URL, headers=HEADERS)
    
    if response.status_code == 200:
        try:
            data = response.json().get("data", [])
            return {task["text"]: task["id"] for task in data if "text" in task}  # Ensure "text" key exists
        except json.JSONDecodeError as e:
            print(f"❌ JSON decoding error when fetching existing tasks: {e}")
            return {}
    
    print("❌ Failed to retrieve existing tasks from Habitica")
    return {}

# Create a new task in Habitica
def create_task(task):
    if "text" not in task:
        print(f"⚠️ Skipping task: Missing 'text' field -> {task}")
        return

    response = requests.post(HABITICA_API_URL, headers=HEADERS, json=task)
    
    if response.status_code == 201:
        print(f"✅ Task created: {task['text']}")
    else:
        print(f"❌ Failed to create task {task['text']}: {response.json()}")

# Sync Habitica tasks from GitHub
def sync_habitica_tasks():
    existing_tasks = get_existing_tasks()
    new_tasks = fetch_github_tasks()

    for task in new_tasks:
        if "text" not in task:
            print(f"⚠️ Skipping invalid task: {task}")  # Skip malformed tasks
            continue

        if task["text"] in existing_tasks:
            print(f"🔄 Task already exists: {task['text']}")
        else:
            create_task(task)

if __name__ == "__main__":
    sync_habitica_tasks()