import os
from typing import _GenericAlias, Union

from .types import TYPE_CAST


def type_looks_optional(annotation):
    """Return True if annotation looks like it was created with Optional"""
    # Optional is just an alias for Union[NoneType, <type>] and this information
    # is lost by the time we can inspect the annoation
    if hasattr(annotation, "__origin__") and annotation.__origin__ is Union and type(None) in annotation.__args__:
        return True
    return False


def not_optional_type(annotation):
    """For an Optional[<type>] return <type>"""
    if not type_looks_optional(annotation):
        return annotation
    return annotation.__origin__[tuple(a for a in annotation.__args__ if a is not type(None))]


def load_env_var(var_name, var_annotation=None, var_value=None):
    """Return the value of `var_name` from the environment

    if `var_annotation` exists, the environment string will be cast into that type
        if the annotation was Optional, the variable does not need to exist in the environment.
        if it does not exist but a val_value was supplied, it will be used as the return value
        if val_value doesn't exist or didn't supply a value, None will be returned
    if `var_value` exists and is a callable, it will be used to cast the environment value
        of var_value. If it is not callable, its value will be used as a default value if needed.
        All of this is done after checking the annotation.
    """
    annotation = not_optional_type(var_annotation)
    is_optional = (annotation != var_annotation) or (var_value is not None) or (var_value is not None and not callable(var_value))

    raw_value = os.getenv(var_name)
    if raw_value is None:
        if not is_optional:
            raise NameError(f"{var_name!r} was not set in the environment")
        if not callable(var_value):
            return var_value
        return None

    if type(annotation) is _GenericAlias:
        possible_constructors = [TYPE_CAST.get(ann, ann) for ann in annotation.__args__]
    else:
        possible_constructors = [TYPE_CAST.get(annotation, annotation)]
    if callable(var_value):
        possible_constructors.append(var_value)

    failed_attempts = []
    for constructor in possible_constructors:
        try:
            value = constructor(raw_value)
            break
        except Exception as why:
            failed_attempts.append(f"{var_name!r} ({raw_value!r}) could not be cast to {constructor}: {why}")
    else:
        if not is_optional:
            raise ValueError(f"Failed to load {var_name!r}:\n{chr(10).join((fail for fail in failed_attempts))}")
        if not callable(var_value):
            value = var_value
        else:
            value = None

    return value
