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
        return self.sheet_scopes

    @sheet_scopes.setter
    def sheet_scopes(self, new_scopes):
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
                        "A value within the sheet_scopes variable is not valid\n"
                        "Check here for possible scope values https://developers.google.com/sheets/api/guides/authorizing"
                    )

        elif isinstance(new_scopes, str):
            if new_scopes not in possible_sheet_scopes:
                raise ValueError(
                    "The sheet_scopes variable is not valid\n"
                    "Check here for possible scope values https://developers.google.com/sheets/api/guides/authorizing"
                )

        else:
            raise TypeError('The sheet_scopes variable should be of type list or str')

        self.sheet_scopes = new_scopes