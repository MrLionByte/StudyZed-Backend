from enum import Enum

from .._common import load_env_var

class EnvEnum(Enum):

    def __init__(self, *args):
        member_annotation = getattr(self, "__annotations__", {}).get(self.name)
        value = args[0] if args else str
        self._value_ = load_env_var(self.name, member_annotation, value)
