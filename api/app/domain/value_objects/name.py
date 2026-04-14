import re

from pydantic import BaseModel, field_validator, model_validator


class Name(BaseModel):
    value: str = ""
    first_name: str
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_required_names(cls, v, info):
        field = info.field_name.replace("_", " ").title()

        if not v:
            raise ValueError(f"{field} cannot be empty")
        if len(v) < 2:
            raise ValueError(f"{field} must be at least 2 characters")
        if len(v) > 48:
            raise ValueError(f"{field} must be at most 48 characters")
        if not re.match(r"^[a-zA-ZÀ-ÿ\s'\-]+$", v):
            raise ValueError(f"{field} contains invalid characters")
        if re.search(r"[\s'\-]{2,}", v):
            raise ValueError(f"{field} cannot have consecutive special characters")
        if v[0] in " '-" or v[-1] in " '-":
            raise ValueError(f"{field} cannot start or end with a special character")

        return v.title()

    @model_validator(mode="after")
    def validate_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        if len(full_name) > 50:
            raise ValueError("Full name must be at most 50 characters")
        self.value = full_name
        return self

    def __str__(self) -> str:
        return self.value