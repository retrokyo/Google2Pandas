from googleapiclient.discovery import build
from google.oauth2 import service_account

import os

from google2pandas.helpers import ValidateSetterProperty, scope_validation


class SheetRelay:
    def __init__(
        self,
        key_file=None,
        sheet_scopes="https://www.googleapis.com/auth/spreadsheets.readonly",
        drive_scopes="https://www.googleapis.com/auth/drive.readonly",
    ):
        self.sheet_scopes = sheet_scopes
        self.key_file = key_file
        self.drive_scopes = drive_scopes

    @ValidateSetterProperty
    def sheet_scopes(self, new_scopes):
        possible_sheet_scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]

        return scope_validation(new_scopes, possible_sheet_scopes)

    @ValidateSetterProperty
    def key_file(self, input_key_file):
        if input_key_file == None:
            key_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        else:
            key_file_path = input_key_file

        if not os.path.isfile(input_key_file):
            raise OSError(
                "Either the enviroment variable GOOGLE_APPLICATION_CRDENTIALS is incorrect or does not exist,\n"
                "or the key file path inputted does not exist"
            )

        return key_file_path
