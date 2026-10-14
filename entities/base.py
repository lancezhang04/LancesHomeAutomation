from pydantic import BaseModel


# TODO: need to consider what states need to be stored, and how they cna be stored/updated
"""
For instance, for a shade, we might want info on whether it's currently open or close.
However, we can't simply store that value and assume it to be true the next time we need it - 
there might have been a manual adjustment/system reboot. So how can we retrieve the ground 
truth value? Would we need access to the adapter class?
"""


class Entity(BaseModel):

    id: str
    type: str  # TODO: create enum for this
