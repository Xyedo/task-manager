
from typing import Annotated, get_args, get_origin
from pydantic import BaseModel, SkipValidation
import os

class Model(BaseModel):
    def __init_subclass__(cls, **kwargs):
        if os.getenv("BYPASS_SECURITY", "FALSE") != "TRUE":
            return super().__init_subclass__(**kwargs)
        
        for name, annotation in cls.__annotations__.items():
            if name.startswith("_"):  # exclude protected/private attributes
                continue
            if get_origin(annotation) is Annotated:
                args = get_args(annotation)
                new_args = args + (SkipValidation,)
                cls.__annotations__[name] = Annotated.__class_getitem__(new_args)
            else:
                cls.__annotations__[name] = Annotated[annotation, SkipValidation]
