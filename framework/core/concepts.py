from pydantic import BaseModel, Field


class SizeBox(BaseModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class Position(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
