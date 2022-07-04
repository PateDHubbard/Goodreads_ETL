from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def get_google_drive_auth():
    """Initializes the Google drive 'drive' object. """
    gauth = GoogleAuth()

    gauth.LoadCredentialsFile("credentials.json")

    if gauth.credentials is None:
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})
        gauth.LocalWebserverAuth()

    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("credentials.json")

    return gauth


def get_google_drive():
    gauth = get_google_drive_auth()
    drive = GoogleDrive(gauth)
    return drive


def get_files_in_folder(drive, folder_id, trimmed=False):
    file_list = drive.ListFile(
        {'q': f"'{folder_id}' in parents and trashed=false"}
        ).GetList()
    if not trimmed:
        return file_list
    else:
        return {file["title"]: file["id"] for file in file_list}


def download_file(drive, folder_id, file_name):
    file_list = get_files_in_folder(drive, folder_id)
    for file in file_list:
        if file["title"] == file_name:
            file.GetContentFile(file["title"])


def upload_new_file_to_drive(drive, folder_id, local_path):
    new_file = drive.CreateFile({'parents': [{'id': folder_id}]})
    new_file.SetContentFile(local_path)
    new_file.Upload()


def overwrite_existing_file_in_drive(drive, file_id, local_path):
    """Overwrites the existing Google drive file."""
    update_file = drive.CreateFile({'id': file_id})
    update_file.SetContentFile(local_path)
    update_file.Upload()


def add_file_to_drive(drive, file_name, folder_id):
    existing_files = get_files_in_folder(drive, folder_id, trimmed=True)
    if file_name in existing_files.keys():
        file_id = existing_files[file_name]
        overwrite_existing_file_in_drive(drive, file_id, file_name)
    else:
        upload_new_file_to_drive(drive, folder_id, file_name)
