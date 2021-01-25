from googlesheet2pandas.sheetrelay import SheetRelay

import pytest

from typing import Type

def test_sheetrelay_initialization():
    sheet_relay: Type[SheetRelay] = SheetRelay()