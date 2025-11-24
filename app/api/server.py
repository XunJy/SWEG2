from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.db import crud
from app.db.models import Booking, Role, init_db

app = FastAPI(title="Room Booking System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


# -------------------------
# Schemas
# -------------------------


class HealthResponse(BaseModel):
    status: str


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: Role = Role.attendee


class UserRead(BaseModel):
    id: str
    full_name: str
    email: str
    role: Role
    created_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class RoomCreate(BaseModel):
    name: str
    building: str | None = None
    capacity: int
    facilities: List[str] = Field(default_factory=list)


class RoomRead(BaseModel):
    id: str
    name: str
    building: str | None = None
    capacity: int
    facilities: List[str]


class BookingCreate(BaseModel):
    organiser_id: str
    room_id: str
    start_time: datetime
    end_time: datetime
    title: str
    description: str | None = None
    is_public: bool = True


class BookingRead(BaseModel):
    id: str
    organiser_id: str
    room_id: str
    start_time: datetime
    end_time: datetime
    title: str
    description: str | None = None
    is_public: bool
    room_name: str
    building: str | None = None
    capacity: int
    attendee_count: int


class RegistrationRead(BaseModel):
    user_id: str
    booking_id: str
    is_organiser: bool
    registered_at: datetime


# -------------------------
# Routes
# -------------------------


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/users", response_model=UserRead, status_code=201)
def create_user(data: UserCreate):
    try:
        user = crud.create_user(
            full_name=data.full_name,
            email=data.email,
            password=data.password,
            role=data.role,
        )
        return UserRead(**user.__dict__)
    except ValueError as exc:  # duplicate email
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/users", response_model=List[UserRead])
def list_users():
    return [UserRead(**u.__dict__) for u in crud.list_users()]


@app.post("/login", response_model=UserRead)
def login(data: LoginRequest):
    user = crud.authenticate(email=data.email, password=data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserRead(**user.__dict__)


@app.post("/rooms", response_model=RoomRead, status_code=201)
def create_room(data: RoomCreate):
    try:
        room = crud.create_room(
            name=data.name,
            building=data.building,
            capacity=data.capacity,
            facilities=data.facilities,
        )
        return RoomRead(**room.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/rooms", response_model=List[RoomRead])
def list_rooms():
    return [RoomRead(**room.__dict__) for room in crud.list_rooms()]


@app.get("/rooms/{room_id}", response_model=RoomRead)
def get_room(room_id: str):
    room = crud.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomRead(**room.__dict__)


@app.post("/bookings", response_model=BookingRead, status_code=201)
def create_booking(data: BookingCreate):
    try:
        booking = crud.create_booking(
            organiser_id=data.organiser_id,
            room_id=data.room_id,
            start_time=data.start_time,
            end_time=data.end_time,
            title=data.title,
            description=data.description,
            is_public=data.is_public,
        )
        return _serialize_booking(booking)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/bookings", response_model=List[BookingRead])
def list_bookings():
    bookings = crud.list_bookings()
    return [_serialize_booking(booking) for booking in bookings]


@app.get("/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: str):
    booking = crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _serialize_booking(booking)


@app.post(
    "/bookings/{booking_id}/register",
    response_model=RegistrationRead,
    status_code=201,
)
def register_for_booking(booking_id: str, user_id: str):
    try:
        registration = crud.register_for_booking(
            booking_id=booking_id, user_id=user_id
        )
        return RegistrationRead(**registration.__dict__)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/bookings/{booking_id}/attendees",
    response_model=List[RegistrationRead],
)
def list_attendees(booking_id: str):
    if not crud.get_booking(booking_id):
        raise HTTPException(status_code=404, detail="Booking not found")
    regs = crud.registrations_for_booking(booking_id)
    return [RegistrationRead(**reg.__dict__) for reg in regs]


# -------------------------
# Helpers
# -------------------------


def _serialize_booking(booking: Booking) -> BookingRead:
    room = crud.get_room(booking.room_id)
    attendee_count = len(crud.registrations_for_booking(booking.id))
    return BookingRead(
        id=booking.id,
        organiser_id=booking.organiser_id,
        room_id=booking.room_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        title=booking.title,
        description=booking.description,
        is_public=booking.is_public,
        room_name=room.name if room else "",
        building=room.building if room else None,
        capacity=room.capacity if room else 0,
        attendee_count=attendee_count,
    )
