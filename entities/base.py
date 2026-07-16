from pydantic import BaseModel


class Entity(BaseModel):

    id: str
    type: str  # TODO: create enum for this
