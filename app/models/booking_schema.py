from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingCreate(BaseModel):
    room_id: str
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    public: bool = False # Bookings default to private

# Response includes all booking details (BookingCreate) and booking_id
class BookingResponse(BookingCreate):
    booking_id: str

    # Pydantic configuration to work with ORM objects (tuples, dictionaries, python classes)
    class Config:
        from_attributes = True
