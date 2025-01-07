from dataclasses import _MISSING_TYPE as DATACLASS_MISSING
from typing import Dict, Type
from typing_extensions import Protocol

from .._common import load_env_var


class DataClass(Protocol):
    """DataClass type

    Since dataclasses are't actually part of the mro, just check that
    expected methods exist
    """
    __dataclass_fields__: Dict


def loadenv_into_dataclass(dataklass: Type[DataClass]) -> DataClass:
    """Return dataklass, instantiated with values from the environment"""
    dataklass_envfields = {}
    for var_in_env, var_in_dataklass in dataklass.__dataclass_fields__.items():
        if not isinstance(var_in_dataklass.default, DATACLASS_MISSING):
            dataklass_var_value = var_in_dataklass.default
        elif not isinstance(var_in_dataklass.default_factory, DATACLASS_MISSING):
            dataklass_var_value = var_in_dataklass.default_factory
        else:
            dataklass_var_value = None
        dataklass_envfields[var_in_env] = load_env_var(var_in_env,
                                                        # dataclass fields must have some annotation
                                                        var_annotation=var_in_dataklass.type,
                                                        var_value=dataklass_var_value)
    return dataklass(**dataklass_envfields)
