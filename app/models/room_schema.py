from pydantic import BaseModel
from typing import Optional

class RoomCreate(BaseModel):
    number: str
    building: str
    capacity: int

# Allow individual fields to be optional for updates
# (don't have to update all room attributes at a time)
class RoomUpdate(RoomCreate):
    number: str | None = None
    building: str | None = None
    capacity: int | None = None
    
class RoomResponse(BaseModel):
    room_id: str # This is auto-gen so not required when creating or updating rooms
    number: str
    building: str
    capacity: int
