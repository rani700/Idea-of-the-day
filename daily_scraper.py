import os
import subprocess
from datetime import datetime
from azure.storage.blob import BlobServiceClient

# --- Configuration ---
AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=ideasarchivestorage;AccountKey=PwsKZGHbXnB3Jski+NEwAIZR8Sv4S3MEA+iqwXz2yaKTE1XBxXLCk7tsIWiSE3zCrgIOCO/V7SUa+AStL1KE7g==;EndpointSuffix=core.windows.net"
AZURE_CONTAINER_NAME = "articles"
URL_TO_SCRAPE = "https://www.ideabrowser.com/idea-of-the-day"

def scrape_and_upload():
    """
    Scrapes the website, saves it to a dated file, 
    and uploads it to Azure Blob Storage.
    """
    if not AZURE_CONNECTION_STRING or "YOUR_AZURE" in AZURE_CONNECTION_STRING:
        print("❌ Error: Please set your AZURE_CONNECTION_STRING.")
        return

    # 1. Create a date-stamped filename
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    local_file_name = f"{today_str}.html"

    # 2. Run the single-file command to scrape the site
    print(f"Scraping {URL_TO_SCRAPE} into {local_file_name}...")
    # Dynamically find the Chromium executable path
    try:
        result = subprocess.run([
            "find", "/ms-playwright", "-path", "*chrome-linux/chrome", "-type", "f"
        ], capture_output=True, text=True, check=True)
        chromium_path = result.stdout.strip().split('\n')[0]
    except Exception as e:
        print(f"❌ Could not find Chromium executable: {e}")
        return

    command = [
        "npx", "single-file",
        "--browser-executable-path", chromium_path,
        URL_TO_SCRAPE,
        local_file_name
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Scrape successful.")
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return

    # 3. Upload the file to Azure Blob Storage
    print(f"Uploading {local_file_name} to Azure container '{AZURE_CONTAINER_NAME}'...")
    try:
        # Create a client to interact with the blob storage
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=local_file_name)

        with open(local_file_name, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
            
        print("✅ Upload successful.")
    except Exception as e:
        print(f"❌ Azure upload failed: {e}")
        return
    finally:
        # 4. Clean up the local file
        if os.path.exists(local_file_name):
            os.remove(local_file_name)
            print(f"Cleaned up local file: {local_file_name}")

if __name__ == "__main__":
    scrape_and_upload()
