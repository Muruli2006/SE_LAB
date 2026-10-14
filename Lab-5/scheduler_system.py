"""Manage conference room reservations and equipment."""

from datetime import datetime
import itertools
import json

reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
RESERVATION_COUNTER = itertools.count(1)


def _parse_slot(time_slot):
    """Parse and validate time slot format and bounds.

    Returns (start_hour, end_hour).
    """
    try:
        start, end = time_slot.split("-")
        start_hour = int(start)
        end_hour = int(end)
    except (ValueError, AttributeError):
        raise ValueError("Time slot must use the format HH-HH.") from None

    if start_hour < 0 or start_hour >= 24 or end_hour <= 0 or end_hour > 24:
        raise ValueError("Hours must be between 0 and 24.")

    if start_hour >= end_hour:
        raise ValueError("End time must be later than start time.")

    return start_hour, end_hour


def schedule_room(room_id, time_slot, equipment_list=None):
    """Schedule a room and allocate the requested equipment."""
    if equipment_list is None:
        equipment_list = []

    start_hour, end_hour = _parse_slot(time_slot)

    for reservation in reservations.values():
        if reservation["room"] == room_id:
            res_start, res_end = _parse_slot(reservation["slot"])
            if max(start_hour, res_start) < min(end_hour, res_end):
                conflicts.append(
                    f"{room_id} double-booked at {time_slot}"
                )
                return None

    equipment_needed = {}
    for equipment in equipment_list:
        if equipment not in equipment_pool:
            raise ValueError(f"Unknown equipment: {equipment}")
        equipment_needed[equipment] = equipment_needed.get(equipment, 0) + 1

    for equipment, count in equipment_needed.items():
        if equipment_pool[equipment] < count:
            raise ValueError(f"No {equipment} available.")

    for equipment in equipment_list:
        equipment_pool[equipment] -= 1

    reservation_id = next(RESERVATION_COUNTER)
    reservations[reservation_id] = {
        "room": room_id,
        "slot": time_slot,
        "equipment": equipment_list.copy(),
    }

    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its allocated equipment."""
    if reservation_id not in reservations:
        return False

    reservation = reservations.pop(reservation_id)

    for equipment in reservation["equipment"]:
        equipment_pool[equipment] += 1

    return True


def slot_hours(time_slot):
    """Calculate the duration of a time slot in hours."""
    start_hour, end_hour = _parse_slot(time_slot)
    return end_hour - start_hour


def export_schedule(file="schedule.json"):
    """Export current reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as output_file:
        json.dump(reservations, output_file, indent=4)


def log_conflicts(file="conflicts.log"):
    """Append conflicts to a log and display its contents."""
    with open(file, "a", encoding="utf-8") as log_file:
        for conflict in conflicts:
            log_file.write(f"{datetime.now()} {conflict}\n")

    with open(file, "r", encoding="utf-8") as log_file:
        print(log_file.read())


def main():
    """Run the room scheduler demonstration."""
    schedule_room("Board-1", "09-11")
    schedule_room("Board-1", "09-11")

    reservation_id = schedule_room("Huddle-3", "14-16")
    if reservation_id is not None:
        print(
            "Slot length:",
            slot_hours(reservations[reservation_id]["slot"]),
        )

    cancel_reservation(77)

    slot = (
        input("Slot for Board-2, like 10-12 (Enter for 10-12): ")
        or "10-12"
    )

    try:
        schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as error:
        print(f"Booking failed: {error}")

    export_schedule()
    log_conflicts()

    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
