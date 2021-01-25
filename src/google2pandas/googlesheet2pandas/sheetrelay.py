# TO DO DOCUMENTATION

from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd

import os
from typing import Optional, Any, ClassVar

from google2pandas.helpers import ValidateSetterProperty, scope_validation
from google2pandas._typing import PathLike, StringOrList, ColumnId


class SheetRelay:

    sheet_scopes: ClassVar[list[str]] = ["https://www.googleapis.com/auth/spreadsheets"]
    drive_scopes: ClassVar[list[str]] = [
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    def __init__(
        self,
        key_file: Optional[PathLike] = None,
        page_size: int = 100,
        **kwargs: Any,
    ) -> None:
        self.key_file = key_file
        self._sheet_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(self.sheet_scopes)
        self._drive_credentials = service_account.Credentials.from_service_account_file(
            self.key_file
        ).with_scopes(self.drive_scopes)
        self._sheet_service = build(
            "sheets",
            "v4",
            credentials=self._sheet_credentials,
            http=kwargs.get("http", None),
            developerKey=kwargs.get("developerKey", None),
            model=kwargs.get("model", None),
            cache_discovery=kwargs.get("cache_discovery", True),
            cache=kwargs.get("cache", None),
        )
        self._drive_service = build(
            "drive",
            "v3",
            credentials=self._drive_credentials,
            http=kwargs.get("http", None),
            developerKey=kwargs.get("developerKey", None),
            model=kwargs.get("model", None),
            cache_discovery=kwargs.get("cache_discovery", True),
            cache=kwargs.get("cache", None),
        )
        self._file_list = self._get_file_list(page_size)

    # Instace Variable Functions
    @ValidateSetterProperty
    def key_file(self, input_key_file: PathLike) -> PathLike:
        if input_key_file == None:
            key_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        else:
            key_file_path = input_key_file

        if not os.path.isfile(key_file_path):
            raise OSError(
                "Either the enviroment variable GOOGLE_APPLICATION_CRDENTIALS is incorrect or does not exist,\n"
                "or the key file path inputted does not exist"
            )

        return key_file_path

    def _get_file_list(self, page_size: int) -> list[dict]:
        response = (
            self._drive_service.files()
            .list(
                pageSize=page_size,
                q="mimeType='application/vnd.google-apps.spreadsheet'",
            )
            .execute()
        )

        file_list = response["files"]

        while response["incompleteSearch"]:
            response = (
                self._drive_service.files()
                .list(
                    pageSize=page_size,
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageToken=response["nextPageToken"],
                )
                .execute()
            )

            file_list + response["files"]

        return file_list

    # Helper Functions
    def _colnum_to_colstr(self, colnum: int) -> str:
        colstr = ""
        while colnum > 0:
            colnum, r = divmod(colnum - 1, 26)
            colstr = chr(65 + r) + colstr

        return colstr

    def _colstr_to_colnum(self, colstr: str) -> int:
        colnum = 0
        for letter in colstr:
            num = num * 26 + (ord(letter.upper()) - ord("A")) + 1

        return colnum

    def _get_spreadsheet_id(self, spreadsheet_name: str) -> str:
        try:
            spreadsheet_id = next(
                file["id"]
                for file in self._file_list
                if file["name"] == spreadsheet_name
            )

        except StopIteration:
            raise Exception("Failed to find file {0} in drive".format(spreadsheet_name))

        return spreadsheet_id

    def _clear_sheet(
        self,
        spreadsheet_name: str,
        sheet_name: StringOrList = "Sheet1",
        by_id: bool = False,
    ):
        if by_id:
            spreadsheet_id = spreadsheet_name
        else:
            spreadsheet_id = self._get_spreadsheet_id(spreadsheet_name)

        if isinstance(sheet_name, list):
            for sheet in sheet_name:
                self._sheet_service.spreadsheets().values().batchClear(
                    spreadsheetId=spreadsheet_id, ranges=sheet
                ).execute()

        elif isinstance(sheet_name, str):
            self._sheet_service.spreadsheets().values().batchClear(
                spreadsheetId=spreadsheet_id, ranges=sheet
            ).execute()

        else:
            raise TypeError("Sheet name variable must be of type str or list")

    # Main Functions
    def df_to_sheet(
        self,
        df: pd.DataFrame,
        spreadsheet_name: str,
        sheet_name: StringOrList = "Sheet1",
        return_response: bool = False,
        by_id: bool = False,
        **kwargs: Any,
    ) -> Optional[dict]:
        if by_id:
            spreadsheet_id = spreadsheet_name
        else:
            spreadsheet_id = self._get_spreadsheet_id(spreadsheet_name)

        sheet_data = [df.columns.values.tolist()] + df.values.tolist()
        colstr = self._colnum_to_colstr(df.shape[1])
        sheet_request_body = {"values": sheet_data}

        spreadsheet = (
            self.sheet_service.spreadsheets()
            .get(spreadsheetId=spreadsheet_id)
            .execute()
        )
        if sheet_name in [
            sheet["properties"]["title"] for sheet in spreadsheet["sheets"]
        ]:
            self._clear_sheet(spreadsheet_id, by_id=True)

        else:
            raise Exception("sheet does not exist")

        sheet_write_request = (
            self._sheet_service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range="{0}!A1:{1}{2}".format(sheet_name, colstr, df.shape[0] + 1),
                valueInputOption=kwargs.get("value_input", "RAW"),
                includeValuesInResponse=kwargs.get("include_values_in_response", False),
                responseValueRenderOption=kwargs.get(
                    "responseValueRenderOption", "FORMATTED_VALUE"
                ),
                responseDateTimeRenderOption=kwargs.get(
                    "response_date_time_render_option", "SERIAL_NUMBER"
                ),
                body=sheet_request_body,
            )
        )

        try:
            response = sheet_write_request.execute()

        except Exception as e:
            print(e)

        if return_response:
            return response

    def sheet_to_df(
        self,
        spreadsheet_name: str,
        start_col: ColumnId,
        end_col: ColumnId,
        sheet_name: StringOrList = "Sheet1",
        blank_cells: bool = False,
        first_row_header: bool = True,
        major_dimensions: str = "ROWS",
        start_row: int = 1,
        end_row: Optional[int] = None,
        by_id: bool = False,
        **kwargs: Any,
    ) -> pd.DataFrame:
        if by_id:
            spreadsheet_id = spreadsheet_name
        else:
            spreadsheet_id = self._get_spreadsheet_id(spreadsheet_name)

        # Start Column Variables
        if isinstance(start_col, str):
            start_col_num = self._colstr_to_colnum(start_col)
            start_col_str = start_col

        elif isinstance(start_col, int):
            start_col_num = start_col
            start_col_str = self._colnum_to_colstr(start_col)

        else:
            raise TypeError("start_col variable must be of type int or str")

        # End Column Varibales
        if isinstance(end_col, str):
            end_col_num = self._colstr_to_colnum(end_col)
            end_col_str = end_col

        elif isinstance(end_col, int):
            end_col_num = end_col
            end_col_str = self._colnum_to_colstr(end_col)

        else:
            raise TypeError("end_col variable must be of type int or str")

        # Start Cell
        if isinstance(start_row, int):
            start_cell = start_col_str + str(start_row)

        else:
            raise TypeError("start_row variable must be of type int")

        # End Cell
        if isinstance(end_row, int):
            end_cell = end_col_str + str(end_row)

        elif isinstance(end_row, type(None)):
            end_cell = end_col_str

        else:
            raise TypeError("end_row variable must be of type int")

        # Number of Columns
        num_of_cols: int = (end_col_num - start_col_num) + 1

        sheet_write_request = (
            self._sheet_service.spreadsheets()
            .values()
            .get(
                spreadsheetId=spreadsheet_id,
                range="{0}!{1}:{2}".format(
                    sheet_name,
                    start_cell,
                    end_cell,
                    majorDimensions=major_dimensions,
                ),
                valueRenderOption=kwargs.get("value_render_option", "FORMATTED_VALUE"),
                dateTimeRenderOption=kwargs.get(
                    "datetime_render_option", "SERIAL_NUMBER"
                ),
            )
        )

        try:
            response = sheet_write_request.execute()

        except Exception as e:
            print(e)

        if not blank_cells:
            if first_row_header:
                df_data = response["values"][1:]
                df_col = response["values"][0]

            else:
                df_data = response["values"]
                df_col = [self._colnum_to_colstr(i) for i in range(num_of_cols)]

        df = pd.DataFrame(data=df_data, columns=df_col)

        return df
