from typing import Union, TypeVar
import os

#Path Like
PathLike = TypeVar("PathLike", str, bytes, os.PathLike)

#Multitype arguments
StringOrList = Union[str, list[str]]
ColumnId = Union[str, int]