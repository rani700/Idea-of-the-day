import os
from flask import Flask, render_template_string, Response
from azure.storage.blob import BlobServiceClient

# --- Configuration ---
# The app will get this from the Azure App Service configuration later
AZURE_CONNECTION_STRING = os.environ.get("AZURE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = "articles"

app = Flask(__name__)

# --- HTML Template for the homepage ---
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archived Ideas</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }
        h1 { color: #0056b3; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 0.5em 0; padding: 1em; background-color: #fff; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        a { text-decoration: none; color: #007bff; font-size: 1.2em; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Archived "Idea of the Day"</h1>
    <ul>
        {% for blob in blobs %}
            <li><a href="/view/{{ blob.name }}">{{ blob.name.replace('.html', '') }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

# --- App Routes ---

@app.route('/')
def index():
    """Homepage: Lists all articles from Azure Blob Storage."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
    
    # Get list of blobs and sort them in reverse order (newest first)
    blob_list = sorted(container_client.list_blobs(), key=lambda b: b.name, reverse=True)
    
    return render_template_string(INDEX_TEMPLATE, blobs=blob_list)

@app.route('/view/<string:filename>')
def view_article(filename):
    """Viewer: Fetches and displays the content of a specific article."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=AZURE_CONTAINER_NAME, blob=filename)
    
    try:
        # Download the blob's content
        downloader = blob_client.download_blob()
        html_content = downloader.readall()
        # Return the content as an HTML response
        return Response(html_content, mimetype='text/html')
    except Exception as e:
        return f"Error: Could not find or load article '{filename}'. Details: {e}", 404