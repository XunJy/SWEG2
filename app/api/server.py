from typing import List
from fastapi import FastAPI, HTTPException
from app.models.user import *
from pydantic import BaseModel

from app.models.booking import *
from app.models.booking_schema import *
from app.models.room import *
from app.models.room_schema import *
from app.models.invite import *
from app.models.user_booking import *

app = FastAPI()

# -------------------------
# Root
# -------------------------
@app.get("/")
def read_root():
    return {"message": "add /docs to the URL to get the api docs"}

# -------------------------
# RESPONSE MODELS
# -------------------------
#this is for returning simple messages or class objects after performing actions
class MessageResponse(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreateResponse(BaseModel):
    message: str
    user_id: str
    recovery_code: str

class InviteCreate(BaseModel):
    booking_id: str
    user_email: str

class UserBookingInfo(BaseModel):
    user: UserRead
    organiser: bool

class BookingInfo(BaseModel):
    booking_id: str
    organiser: bool


# -------------------------
# USER ROUTES
# -------------------------

# Login User
@app.post("/login", response_model=UserRead)
def api_login_user(data: LoginRequest):
    user = read_user_by_email(data.email) 
    if not user:
        # No user found with that email
        raise HTTPException(status_code=404, detail="User not found")
    
    if not check_password(user["password"], data.password):
        # Password does not match
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Successful login
    return UserRead(**user)


# Create User
@app.post("/users", response_model=UserCreateResponse)
def api_create_user(user: UserCreate):
    user_id, recovery_code = create_user(user)

    if user_id:
        return {
            "message": "User created successfully",
            "user_id": user_id,
            "recovery_code": recovery_code
        }

    raise HTTPException(status_code=400, detail="User creation failed")


# Read User by user ID
@app.get("/users/{user_id}", response_model=UserRead)
def api_get_user(user_id: str):
    # Find user by ID
    all_users = read_user_by_id(user_id) 
    if all_users:
        return UserRead(**all_users)
    raise HTTPException(status_code=404, detail="User not found")


# Read User by EMail 
@app.get("/users/email/{email}", response_model=UserRead)
def api_get_user_email(email: str):
    # Find user by ID
    all_users = read_user_by_email(email) 
    if all_users:
        return UserRead(**all_users)
    raise HTTPException(status_code=404, detail="User not found")


# Update Name
@app.put("/users/{user_id}/name", response_model=MessageResponse)
def api_update_name(user_id: str, password: str, new_first: str, new_last: str):
    user = read_user_by_id(user_id)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    update_user_name(user["email"], password, new_first, new_last)
    return MessageResponse(message="Name updated")


# Update Email
@app.put("/users/{user_id}/email", response_model=MessageResponse)
def api_update_email(user_id: str, password: str, new_email: str):
    user = read_user_by_id(user_id)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    update_user_email(user["email"], password, new_email)
    return MessageResponse(message="Email updated")


# Update Password
@app.put("/users/email/{email}/password", response_model=MessageResponse)
def api_update_password_by_email(email: str, recovery_code: str, new_password: str):
    user = read_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["recovery_code"] != recovery_code:
        raise HTTPException(status_code=401, detail="Invalid recovery code")

    update_user_password(email, recovery_code, new_password)
    return MessageResponse(message="Password updated")


# Delete User
@app.delete("/users/{user_id}", response_model=MessageResponse)
def api_delete_user(user_id: str, password: str):
    user = read_user_by_id(user_id)
    if not user or not check_password(user["password"], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    delete_user(user["email"], password)
    return {"message": "Account deleted"}

# -------------------------
# BOOKING ROUTES
# -------------------------

# GET: All public bookings (available events)
@app.get("/bookings/public", response_model=List[BookingResponse])
def api_get_public_bookings(user_id: str):
    try:
        return get_public_bookings(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST: Create a booking
@app.post("/bookings", response_model=BookingResponse)
def api_create_booking(data: BookingCreate):
    try:
        booking_data = create_booking(
            data.room_id,
            str(data.start_time),
            str(data.end_time),
            data.name,
            data.description,
            data.public
        )
        return BookingResponse(**booking_data)
    except ValueError as e:
        print("Error:", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
# GET: Read a booking by booking ID
@app.get("/bookings/{booking_id}", response_model=BookingResponse)
def api_get_booking(booking_id: str):
    booking_data = read_booking(booking_id)
    if not booking_data:
        raise HTTPException(status_code=404, detail="Booking not found")
    return BookingResponse(**booking_data)
    
# DELETE: Delete a booking by ID
@app.delete("/bookings/{booking_id}", response_model=MessageResponse)
def api_delete_booking(booking_id: str):
    try:
        success = delete_booking(booking_id)
        if success:
            return MessageResponse(message="Booking deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    raise HTTPException(status_code=404, detail="Booking not found")

# GET: Read a booking by user ID
@app.get("/bookings/user/{user_id}", response_model=List[BookingResponse])
def api_get_bookings_by_user(user_id: str):
    return read_bookings_by_user(user_id)

# GET: All bookings
@app.get("/bookings")
def api_get_all_bookings():
    try:
        bookings = read_all_bookings()
        return bookings
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# -------------------------
# INVITE ROUTES
# -------------------------
# Create Invite
@app.post("/invites", response_model=Invite)
def api_create_invite(invite: InviteCreate):
    # Look up user by email
    user = read_user_by_email(invite.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    created = create_invite(
        booking_id=invite.booking_id,
        user_id=user["user_id"],  # Use the user_id from email (i.e., email is translated to user_id)
        status='pending'
    )

    if created:
        return created

    raise HTTPException(status_code=400, detail="Invite creation failed")


# Get pending Invites for a specific User
@app.get("/users/{user_id}/invites", response_model=list[Invite])
def api_get_invites_by_user(user_id: str):
    invites = get_invites_by_user(user_id)

    # Filter for pending invites
    pending_invites = [invite for invite in invites if invite.status == "pending"] if invites else []
    return pending_invites


# Accept Invite (Invite ID)
@app.put("/invites/{invite_id}/status/accept", response_model=MessageResponse)
def api_update_invite_status_accept(invite_id: str, new_status: str = "accepted"):
    updated = update_invite_status(invite_id, new_status)
    if updated:
        return MessageResponse(message=f"Invite {invite_id} status updated to {new_status}")
    raise HTTPException(status_code=400, detail="Failed to update invite status")


# Decline Invite (Invite ID)
@app.put("/invites/{invite_id}/status/decline", response_model=MessageResponse)
def api_update_invite_status_decline(invite_id: str, new_status: str = "declined"):
    updated = update_invite_status(invite_id, new_status)
    if updated:
        return MessageResponse(message=f"Invite {invite_id} status updated to {new_status}")
    raise HTTPException(status_code=400, detail="Failed to update invite status")

# -------------------------
# User-Booking Routes
# -------------------------

# CREATE - link users to bookings
    #run this after accpeting an invite to add the user as a participant to the booking
@app.post("/user-bookings", response_model=MessageResponse)
def api_create_user_booking(data: UserBookingCreate):
    try:
        create_user_booking(data.user_id, data.booking_id, data.organiser)
            #organiser defaults to False in the sqlite function if not provided
        return MessageResponse(message="User booking created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create user booking: {str(e)}")

# READ: get users for a booking
@app.get("/bookings/{booking_id}/users", response_model=List[UserBookingInfo])
def api_get_users_for_booking(booking_id: str):
    users = get_users_for_booking(booking_id)
    return [UserBookingInfo(user=user, organiser=organiser) for user, organiser in users]

# READ: get bookings for a user
@app.get("/users/{user_id}/bookings", response_model=List[BookingInfo])
def api_get_bookings_for_user(user_id: str):
    bookings = get_bookings_for_user(user_id)
    return [BookingInfo(booking_id=booking_id, organiser=organiser) for booking_id, organiser in bookings]

# UPDATE: organiser status
@app.put("/user-bookings/{user_id}/{booking_id}", response_model=MessageResponse)
def api_update_booking_admin(user_id: str, booking_id: str, data: UserBookingUpdate):
    try:
        update_user_booking(user_id, booking_id, data.organiser)
        return MessageResponse(message="User booking updated successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update user booking: {str(e)}")

# DELETE: remove user from booking
@app.delete("/user-bookings/{user_id}/{booking_id}", response_model=MessageResponse)
def api_delete_user_booking(user_id: str, booking_id: str):
    try:
        delete_user_booking(user_id, booking_id)
        return MessageResponse(message="User booking deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete user booking: {str(e)}")

# -------------------------
# ROOM ROUTES
# -------------------------

# POST: Create a room
@app.post("/rooms", response_model=RoomResponse)
def api_create_room(data: RoomCreate, user_id: str):
    try:
        room_id = create_room(user_id, data.number, data.building, data.capacity)
        room_data = read_room(room_id)
        return RoomResponse(room_id=room_data[0], number=room_data[1], building=room_data[2], capacity=room_data[3])
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# GET: Get room availability for a specific day (between 9-5pm)
@app.get("/rooms/{room_id}/availability/day")
def api_get_room_day_availability(room_id: str, date: str):
    try:
        # Validate room exists
        room_data = read_room(room_id)
        if not room_data:
            raise HTTPException(status_code=404, detail="Room not found")

        slots = generate_time_slots_for_day(date)
        availability = []

        for start_time, end_time in slots:
            conflict = get_conflicting_bookings(room_id, start_time, end_time)
            availability.append({
                "slot": f"{start_time[-8:]} - {end_time[-8:]}",  # HH:MM:SS format
                "available": not conflict
            })

        return {
            "room_id": room_id,
            "date": date,
            "availability": availability
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# GET: Get all available rooms for a given datetime slot
@app.get("/rooms/available", response_model=List[RoomResponse])
def api_get_available_rooms(start_time: str, end_time: str):
    try:
        rooms = read_rooms()  # Find all rooms
        available_rooms = []

        for r in rooms:
            room_id = r[0]

            # Room is free if there are no conflicting bookings
            is_conflict = get_conflicting_bookings(room_id, start_time, end_time)

            if not is_conflict:
                # Add only truly available rooms
                available_rooms.append(RoomResponse(room_id=r[0],number=r[1],building=r[2],capacity=r[3]))

        return available_rooms

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET: Read a room by ID
@app.get("/rooms/{room_id}", response_model=RoomResponse)
def api_get_room(room_id: str):
    room_data = read_room(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(room_id=room_data[0], number=room_data[1], building=room_data[2], capacity=room_data[3])

# PUT: Update a room
@app.put("/rooms/{room_id}", response_model=MessageResponse)
def api_update_room(room_id: str, data: RoomUpdate, user_id: str):
    try:
        update_room(user_id, room_id, data.number, data.building, data.capacity)
        return MessageResponse(message="Room updated successfully")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# DELETE: Delete a room
@app.delete("/rooms/{room_id}", response_model=MessageResponse)
def api_delete_room(room_id: str, user_id: str):
    try:
        delete_room(user_id, room_id)
        return MessageResponse(message="Room deleted successfully")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# GET: All rooms
@app.get("/rooms", response_model=List[RoomResponse])
def api_get_all_rooms():
    try:
        rooms = read_rooms()
        return [RoomResponse(room_id=r[0], number=r[1], building=r[2], capacity=r[3]) for r in rooms]
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
