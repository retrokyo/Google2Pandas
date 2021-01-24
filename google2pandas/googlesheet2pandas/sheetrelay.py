from googleapiclient.discovery import build
from google.oauth2 import service_account

import os


class SheetRelay:
    def __init__(
        self,
        sheet_scopes="https://www.googleapis.com/auth/spreadsheets.readonly",
        key_file=None,
        drive_scopes="https://www.googleapis.com/auth/drive.readonly",
    ):
        self.sheet_scopes = sheet_scopes

    @property
    def sheet_scopes(self):
        return self.scopes

    @sheet_scopes.setter
    def scopes(self, new_scopes):
        possible_sheet_scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ]

        if isinstance(new_scopes, list):
            for scope in new_scopes:
                if scope not in possible_sheet_scopes:
                    raise ValueError(
                        "A value within the sheet_scopes variable is not valid\nCheck here for possible scopes values https://developers.google.com/sheets/api/guides/authorizing"
                    )

        if new_scopes not in possible_sheet_scopes:
            raise ValueError(
                "The sheet_scopes variables is not valid\nCheck here for possible scopes values https://developers.google.com/sheets/api/guides/authorizing"
            )

        self.scopes = new_scopes