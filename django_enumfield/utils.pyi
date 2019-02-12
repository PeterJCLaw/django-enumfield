from .enum import Enum
from .item import Item

def get_enum_or_404(enum: Enum, slug: str) -> Item: ...

class TemplateErrorException(RuntimeError):
    silent_variable_failure: bool
