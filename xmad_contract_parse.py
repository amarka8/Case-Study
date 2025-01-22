import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


import io
from PyPDF2 import PdfReader

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    FOLDER_ID = '1i437SoUirGOHtasQEnDUG4kcFIPnB9Mo'
    #retrieve all files until none left using pageToken
    files = []
    page_token = None
    while True:
        results = service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf'",
            fields="nextPageToken, files(id, name)", pageToken = page_token).execute()
        
        for file in results.get("files", []):
        # Process change
            print(f'Found file: {file.get("name")}, {file.get("id")}')
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken", None)
        if page_token is None:
            break

    # Count pages and sort files
    # file_page_counts = []
    for file in files:
        file_id = file['id']
        file_name = file['name']
    #     print(file_name)
    # make http request to get files in xmad folder
        request = service.files().get_media(
            fileId=file_id
        )
    # get xmad contracts and filter by length to get contracts
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")
        
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        #write contracts to xmad-contracts
        if(num_pages > 60):
            output_path = os.path.join('./xmad-contracts', file_name)
            input_path = os.path.join('./xmad-files', file_name)
            os.rename(input_path, output_path)


  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()