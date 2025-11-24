import os # For file operations
from app.db.database import init_db, get_db_connection, DB_PATH


# Delete the database file and recreates it before running tests
def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) # Deletes (old) database file
        print("(!) Database reset occured (old db file removed)")

    init_db() # Creates (new) database file and tables
    print("NEW DATABASE INITIALISED.")

# Run DB Tests
def run_tests():
    print("\n--- Initialising Database ---")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        #-------------------------
        # CREATE TESTS
        #-------------------------

        # Insert User Test Data
        print("\n--- Inserting User Data ---")
        cursor.execute("""
                        INSERT INTO user(user_id, first_name, last_name, email, password, recovery_code, admin)
                        VALUES ('user_1', 'Alice', 'Smith', 'alice@example.com', 'password123', 'recovery123', 0);
                    """)
        print("Inserted user_1, Alice Smith")
        
        cursor.execute("""
                        INSERT INTO user(user_id, first_name, last_name, email, password, recovery_code, admin)
                        VALUES ('user_2', 'Bob', 'Ross', 'bob@example.com', 'password321', 'recovery321', 0);
                    """)
        print("Inserted user_2, Bob Ross")
        
        # Insert Room Test Data
        print("\n--- Inserting Room Data ---")
        cursor.execute("""
                        INSERT INTO room(room_id, number, building, capacity)
                        VALUES ('room_1', '101', 'Jack Cole', 15);
                    """)
        print("Inserted room_1, 101 Jack Cole")
        
        # Insert Facility Test Data
        print("\n--- Inserting Facilities Data ---")
        cursor.execute("""
                        INSERT INTO facility(facility_id, name)
                        VALUES ('1', 'Projector');
                    """)
        print("Inserted facility_1, Projector")
        
        cursor.execute("""
                        INSERT INTO facility(facility_id, name)
                        VALUES ('2', 'Whiteboard');
                    """)
        print("Inserted facility_2, Whiteboard")
        
        # Link rooms and facilities
        print("\n--- Linking Rooms and Facilities ---")
        cursor.execute("""
                        INSERT INTO room_facility(room_id, facility_id)
                        VALUES ('room_1', '1');
                    """)
        print("Linked room_1 with facility_1 (projector)")
        cursor.execute("""
                        INSERT INTO room_facility(room_id, facility_id)
                        VALUES ('room_1', '2');
                    """)
        print("Linked room_1 with facility_2 (whiteboard)")
        
        # Insert Booking Test Data
        print("\n--- Inserting Booking Data ---")
        cursor.execute("""
                        INSERT INTO booking(booking_id, room_id, start_time, end_time, name, description)
                        VALUES (
                            'booking_1',
                            'room_1',
                            '2023-10-01 10:00',
                            '2023-10-01 11:00',
                            'Team Meeting',
                            'Discuss project updates'
                        );
                    """)
        print("Inserted booking_1 in room_1")
        
        # Link bookings and users (User 1 is organiser, User 2 is participant)
        print("\n--- Linking Bookings and Users ---")
        cursor.execute("""
                        INSERT INTO user_booking(user_id, booking_id, organiser)
                        VALUES ('user_1', 'booking_1', 1);
                    """)
        print("Linked user_1 (Alice) as organiser of booking_1")
        
        cursor.execute("""
                        INSERT INTO user_booking(user_id, booking_id, organiser)
                        VALUES ('user_2', 'booking_1', 0);
                    """)
        print("Linked user_2 (Bob) as attendee of booking_1")

        # Insert Invite Test Data (User 2 invited to Booking 1)
        cursor.execute("""
                        INSERT INTO invite(invite_id, booking_id, user_id, status)
                        VALUES ('invite_1', 'booking_1', 'user_2', 'pending');
                    """)
        print("Inserted invite_1 for user_2 (Bob) to booking_1")
        
        #-------------------------
        # READ TESTS
        #-------------------------
        
        # All user data has been correctly inserted
        print("\n--- Reading User Data ---")
        cursor.execute("SELECT user_id, first_name, last_name, email, admin FROM user;")
        users = cursor.fetchall()
        print("CHECK Users inserted:")
        for row in users:
            print(f"   - ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Admin: {row[4]}")

        
        # All room data has been correctly inserted
        print("\n--- Reading Room Data ---")
        cursor.execute("SELECT room_id, number, building, capacity FROM room;")
        rooms = cursor.fetchall()
        print("CHECK Rooms inserted:")
        for row in rooms:
            print(f"   - ID: {row[0]}, Number: {row[1]}, Building: {row[2]}, Capacity: {row[3]}")

        
        # All rooms have correct facilities linked
        print("\n--- Reading Room Facility Data ---")
        cursor.execute("SELECT room_id, facility_id FROM room_facility;")
        room_facilities = cursor.fetchall()
        print("CHECK Room-Facility links:")
        for row in room_facilities:
            print(f"   - Room ID: {row[0]}, Facility ID: {row[1]}")
            
        
        # All booking data has been correctly inserted
        print("\n--- Reading Booking Data ---")
        cursor.execute("SELECT booking_id, room_id, start_time, end_time, name, description FROM booking;")
        bookings = cursor.fetchall()
        print("CHECK Bookings inserted:")
        for row in bookings:
            print(
                f"   - Booking ID: {row[0]}, Room: {row[1]}, Time: {row[2]}–{row[3]}, "
                f"Name: {row[4]}, Description: {row[5]}"
            )

        
        # All bookings have correct users linked
        print("\n--- Reading User Booking Data ---")
        cursor.execute("SELECT user_id, booking_id, organiser FROM user_booking;")
        user_bookings = cursor.fetchall()
        print("CHECK User-Booking links (attendance):")
        for row in user_bookings:
            role = "Organiser" if row[2] == 1 else "Participant"
            print(f"   - User ID: {row[0]}, Booking ID: {row[1]} ({role})")

        
        # All invite data has been correctly inserted
        print("\n--- Reading Invite Data ---")
        cursor.execute("SELECT invite_id, booking_id, user_id, status FROM invite;")
        invites = cursor.fetchall()
        print("CHECK Invites inserted:")
        for row in invites:
            print(f"   - Invite ID: {row[0]}, Booking: {row[1]}, User: {row[2]}, Status: {row[3]}")

        
        #-------------------------
        # UPDATE TESTS
        #-------------------------
        
        print("\n--- Updating User Data ---")
        cursor.execute("""
                        UPDATE user
                        SET last_name = 'Ross'
                        WHERE user_id = 'user_1';
                    """)
        
        print("\n--- Reading Updated User Data ---")
        cursor.execute("SELECT * FROM user;")
        print(cursor.fetchall())
        
        
        cursor.execute("""
                        UPDATE invite
                        SET status = 'accepted'
                        WHERE invite_id = 'invite_1';
                    """)
        print("\n--- Reading Updated Invite Data ---")
        cursor.execute("SELECT * FROM invite;")
        print(cursor.fetchall())
        
        #-------------------------
        # DELETE TESTS
        #-------------------------
        print("\n Deleting Room r1 (which should cascade delete bookings, user_bookings, and invites)")
        cursor.execute("DELETE FROM room WHERE room_id = 'room_1';")
        
    # Scope out of context manager, committing & closing connection
    
    # Re-open connection to verify deletions
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        print("\n--- After Cascade Delete: no bookings should exist ---")
        cursor.execute("SELECT * FROM booking;")
        bookings = cursor.fetchall()
        if not bookings:
            print("PASS")
        else:
            print("FAIL")
        
        print("\n--- After Cascade Delete: no facilities should be linked with rooms ---")
        cursor.execute("SELECT * FROM room_facility;")
        room_facilities = cursor.fetchall()
        if not room_facilities:
            print("PASS")
        else:
            print("FAIL")
        
        print("\n--- After Cascade Delete: no users should be associated with bookings ---")
        cursor.execute("SELECT * FROM user_booking;")
        user_bookings = cursor.fetchall()
        if not user_bookings:
            print("PASS")
        else:
            print("FAIL")
        
        print("\n--- After Cascade Delete: no invites pending or accepted should exist ---")
        cursor.execute("SELECT * FROM invite;")
        invites = cursor.fetchall()
        if not invites:
            print("PASS")
        else:
            print("FAIL")
        
        print("\n--- After Cascade Delete: users should still exist ---\n")
        cursor.execute("SELECT * FROM user;")
        users = cursor.fetchall()
        if users:
            print("PASS")
            for user in users:
                print("     ", user)
        else:
            print("FAIL")
        
        print("\n--- ALL DATABASE TESTS COMPLETED ---\n")

# Main: reset the database and run tests
if __name__ == "__main__":
    reset_database()
    # run_tests()
