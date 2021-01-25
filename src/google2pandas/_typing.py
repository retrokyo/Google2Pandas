from typing import Union, TypeVar
import os

#Path Like
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)

#Multitype arguments
StringOrList = TypeVar("StringOrList", str, list)
ColumnId = TypeVar("ColumnId", str, int)