import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("drive", "v3", credentials=creds)


def search_folder_by_name(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])
    return items[0] if items else None


def get_direct_link(file_id):
    return f"https://drive.google.com/drive/folders/{file_id}"


def main():
    service = get_authenticated_service()
    folder_name = input("Enter the folder name: ")
    folder = search_folder_by_name(service, folder_name)
    if folder:
        print(f"Folder found: {folder['name']}")
        direct_link = get_direct_link(folder["id"])
        print(f"Direct link: {direct_link}")
    else:
        print("Folder not found.")


if __name__ == "__main__":
    main()
