"""Functionality to cast strings to arbitraty Python objects

Of most interest is `TYPE_CAST` which is a mapping used to associate type objects with
a callable that can take a string as its only argument and return an object of the same
type.

If the type object *is* the callable used to return its type from a string (e.g.
int()), no entry in `TYPE_CAST` is required.

Type Aliases can be used to create the
same type from multiple different format types (List and PathSepList both return type
List, but parse their strings in different ways).

Entries in `TYPE_CAST` can be added to, modified, or deleted and changes will effect
subsequent environment loading.
"""
import re
from typing import Dict, FrozenSet, List, Sequence, Set, Tuple, Type, TypeVar, Union


# Aliases
CSVList = List
PathSepList = List


def parse_sequence(
    raw_value: str, delimiter: str = ",", bounds: str = "", values_can_be_quoted=True
) -> Sequence[str]:
    """Parse a single string into a sequence of strings.
    This is similar to ast.parse_literal but is meant to support non-python reprs and more types

    raw_value: the string to parse
    delimiter: the token to separate values by. This token is not kept
    bounds: zero, one, or two tokens that signify the start and end of the sequence. These tokens are not kept
        if the empty sting, the start and end are assumed to be the beginning and end of raw_value
        if a single character, it will be looked for to both start and end the sequence
        if two characters, the first one will start the sequence and the second one will end it
    values_can_be_quoted: if True values between delimiters can be surrounded in single or double quotes. These quotes are not kept
        if False any quotes are assumed to be part of the value

    whitespace is assumed to be insignificant and is removed
        unless the delimiter is whitespace, then it is significant but not kept
        unless values_can_be_quoted is True in which case whitespace within quotes are significant and kept
    raw_value is assumed to contain one (to be parsed) sequence
    """
    if not delimiter:
        raise ValueError("Delimiter cannot be empty")
    if len(bounds) < 2:
        bound_start = raw_value.find(bounds[0:1])
        bound_end = raw_value.rfind(bounds[0:1])
    else:
        bound_start = raw_value.find(bounds[0]) + 1
        bound_end = raw_value.find(bounds[1])
    if bound_start < 0 or bound_end < 0 or bound_start > bound_end:
        raise ValueError(f"raw_value does not contain both bounds {bounds}")
    working_value = raw_value[bound_start:bound_end]
    working_value = working_value.strip()

    seq = []
    for item in working_value.split(delimiter):
        item = item.strip()
        if values_can_be_quoted and len(item) > 1 and item[0] == item[-1] and item[0] in ("'", '"'):
            item = item[1:-1]
        if item:
            seq.append(item)
    return seq


def _cast_bool(maybe_bool: str) -> bool:
    maybe_bool = maybe_bool.lower()
    if maybe_bool in ["true", "yes", "y", "on"]:
        return True
    if maybe_bool in ["false", "no", "n", "off"]:
        return False
    raise ValueError(f"{maybe_bool} is not a boolean value")


def _cast_bytes(maybe_bytes: str) -> bytes:
    return bytes(maybe_bytes, sys.getfilesystemencoding())


def _cast_list(maybe_list: str) -> List[str]:
    return parse_sequence(maybe_list, bounds="[]")


def _cast_bare_list(maybe_list: str) -> List[str]:
    return parse_sequence(maybe_list, bounds="",
            values_can_be_quoted=False,
            )


def _cast_path_list(maybe_list: str) -> List[str]:
    return parse_sequence(maybe_list, bounds="",
            delimiter=os.pathsep,
            values_can_be_quoted=False,
            )


def _cast_set(maybe_set: str) -> Set[str]:
    return parse_sequence(maybe_set, bounds="{}")


def _cast_dict(maybe_dict: str) -> Dict[str, str]:
    items = parse_sequence(maybe_dict, bounds="{}", values_can_be_quoted=False)
    yes_dict = dict(parse_sequence(item, bounds="", delimiter=":") for item in items)
    return yes_dict


# if a variable is annotated with one of these types, attempt casting the environment
# value using this callable rather than the type itself
TYPE_CAST = {bool: _cast_bool,
             bytes: _cast_bytes,
             Dict: _cast_dict,
             dict: _cast_dict,
             FrozenSet: frozenset,
             List: _cast_list,
             list: _cast_list,
             CSVList: _cast_bare_list,
             PathSepList: _cast_path_list,
             Set: _cast_set,
             set: _cast_set,
             Tuple: tuple,
            }
