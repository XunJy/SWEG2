from flask import Flask, request, jsonify
from booking import (
    create_booking,
    read_booking,
    read_booking_by_room,
    read_bookings_by_user,
    update_booking_name,
    update_booking_description,
    delete_booking
)

app = Flask(__name__)

@app.post("/booking")
def api_create_booking():
    data = request.json
    booking_id = create_booking(
        room_id=data["room_id"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        name=data["name"],
        description=data.get("description"),
        user_id=data.get("user_id", "system")
    )
    return jsonify({"booking_id": booking_id}), 201


@app.get("/booking/<booking_id>")
def api_read_booking(booking_id):
    booking = read_booking(booking_id)
    return jsonify(booking) if booking else (jsonify({"error": "Not found"}), 404)


@app.get("/room/<room_id>/bookings")
def api_read_by_room(room_id):
    return jsonify(read_booking_by_room(room_id))


@app.get("/user/<user_id>/bookings")
def api_read_by_user(user_id):
    return jsonify(read_bookings_by_user(user_id))


@app.patch("/booking/<booking_id>/name")
def api_update_name(booking_id):
    data = request.json
    update_booking_name(booking_id, data["new_name"], data.get("user_id", "system"))
    return jsonify({"status": "ok"})


@app.patch("/booking/<booking_id>/description")
def api_update_description(booking_id):
    data = request.json
    update_booking_description(booking_id, data["new_description"], data.get("user_id", "system"))
    return jsonify({"status": "ok"})


@app.delete("/booking/<booking_id>")
def api_delete_booking(booking_id):
    delete_booking(booking_id)
    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(debug=True)
# To run the server, use the command:
# python app.py