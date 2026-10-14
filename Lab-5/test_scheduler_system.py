"""Unit tests for Conference Room and Equipment Scheduler."""

import itertools
import json
import os
import unittest
import scheduler_system


class TestSchedulerSystem(unittest.TestCase):
    """Test suite covering functional requirements of scheduler_system."""

    def setUp(self):
        """Reset global module state before each test."""
        scheduler_system.reservations.clear()
        scheduler_system.equipment_pool = {
            "projector": 2,
            "microphone": 4,
            "webcam": 1,
        }
        scheduler_system.conflicts.clear()
        if hasattr(scheduler_system, "RESERVATION_COUNTER"):
            scheduler_system.RESERVATION_COUNTER = itertools.count(1)
        if hasattr(scheduler_system, "NEXT_RESERVATION"):
            scheduler_system.NEXT_RESERVATION = 1

        self.test_json = "test_schedule.json"
        self.test_log = "test_conflicts.log"

    def tearDown(self):
        """Clean up test artifacts."""
        for path in (self.test_json, self.test_log):
            if os.path.exists(path):
                os.remove(path)

    def test_valid_booking(self):
        """Test scheduling a room with valid parameters."""
        res_id = scheduler_system.schedule_room(
            "Board-1", "09-11", ["projector"]
        )
        self.assertIsNotNone(res_id)
        self.assertEqual(res_id, 1)
        self.assertIn(res_id, scheduler_system.reservations)
        res = scheduler_system.reservations[res_id]
        self.assertEqual(res["room"], "Board-1")
        self.assertEqual(res["slot"], "09-11")
        self.assertEqual(res["equipment"], ["projector"])
        self.assertEqual(scheduler_system.equipment_pool["projector"], 1)

    def test_duplicate_room_booking(self):
        """Test duplicate booking triggers a conflict."""
        res_id1 = scheduler_system.schedule_room("Board-1", "09-11")
        self.assertIsNotNone(res_id1)
        res_id2 = scheduler_system.schedule_room("Board-1", "09-11")
        self.assertIsNone(res_id2)
        self.assertEqual(len(scheduler_system.conflicts), 1)
        self.assertIn(
            "Board-1 double-booked at 09-11",
            scheduler_system.conflicts[0],
        )

    def test_overlapping_room_booking(self):
        """Test overlapping slots trigger a conflict."""
        res_id1 = scheduler_system.schedule_room("Board-1", "09-11")
        self.assertIsNotNone(res_id1)
        # 10-12 overlaps with 09-11
        res_id2 = scheduler_system.schedule_room("Board-1", "10-12")
        self.assertIsNone(res_id2)
        self.assertEqual(len(scheduler_system.conflicts), 1)
        self.assertIn(
            "Board-1 double-booked at 10-12",
            scheduler_system.conflicts[0],
        )

    def test_adjacent_slots_no_conflict(self):
        """Test that back-to-back non-overlapping slots succeed."""
        res_id1 = scheduler_system.schedule_room("Board-1", "09-11")
        res_id2 = scheduler_system.schedule_room("Board-1", "11-13")
        self.assertIsNotNone(res_id1)
        self.assertIsNotNone(res_id2)
        self.assertEqual(len(scheduler_system.conflicts), 0)

    def test_invalid_time_format(self):
        """Test that invalid time slot formats raise ValueError."""
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Board-1", 1530)
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Board-1", "morning")
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Board-1", "09:00-11:00")
        with self.assertRaises(ValueError):
            scheduler_system.slot_hours("invalid")

    def test_end_time_earlier_than_start_time(self):
        """Test that invalid hour ranges raise ValueError."""
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Huddle-3", "14-12")
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Huddle-3", "10-10")
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Huddle-3", "23-25")
        with self.assertRaises(ValueError):
            scheduler_system.slot_hours("14-12")

    def test_unknown_equipment(self):
        """Test that requesting unknown equipment raises ValueError."""
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room(
                "Board-1", "09-11", ["laser_pointer"]
            )
        self.assertEqual(len(scheduler_system.reservations), 0)

    def test_equipment_exhaustion(self):
        """Test requesting more equipment than available raises ValueError."""
        # webcam initial count is 1
        res1 = scheduler_system.schedule_room("Room-A", "09-11", ["webcam"])
        self.assertIsNotNone(res1)
        self.assertEqual(scheduler_system.equipment_pool["webcam"], 0)

        # requesting another webcam should fail
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room("Room-B", "09-11", ["webcam"])

        # requesting multiple identical items exceeding stock
        with self.assertRaises(ValueError):
            scheduler_system.schedule_room(
                "Room-C", "09-11", ["projector", "projector", "projector"]
            )
        self.assertEqual(scheduler_system.equipment_pool["projector"], 2)

    def test_successful_cancellation(self):
        """Test cancelling an existing reservation."""
        res_id = scheduler_system.schedule_room(
            "Board-1", "09-11", ["projector"]
        )
        self.assertIn(res_id, scheduler_system.reservations)
        result = scheduler_system.cancel_reservation(res_id)
        self.assertTrue(result)
        self.assertNotIn(res_id, scheduler_system.reservations)

    def test_cancellation_of_nonexistent_reservation(self):
        """Test cancelling a nonexistent reservation returns False safely."""
        result = scheduler_system.cancel_reservation(999)
        self.assertFalse(result)

    def test_equipment_restoration(self):
        """Test that cancellation restores allocated equipment accurately."""
        initial_proj = scheduler_system.equipment_pool["projector"]
        initial_mic = scheduler_system.equipment_pool["microphone"]

        res_id = scheduler_system.schedule_room(
            "Board-1", "09-11", ["projector", "microphone"]
        )
        self.assertEqual(
            scheduler_system.equipment_pool["projector"], initial_proj - 1
        )
        self.assertEqual(
            scheduler_system.equipment_pool["microphone"], initial_mic - 1
        )

        scheduler_system.cancel_reservation(res_id)
        self.assertEqual(
            scheduler_system.equipment_pool["projector"], initial_proj
        )
        self.assertEqual(
            scheduler_system.equipment_pool["microphone"], initial_mic
        )

    def test_json_export(self):
        """Test exporting reservations to JSON file."""
        res_id = scheduler_system.schedule_room(
            "Board-1", "09-11", ["projector"]
        )
        scheduler_system.export_schedule(self.test_json)
        self.assertTrue(os.path.exists(self.test_json))

        with open(self.test_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(str(res_id), data)
        self.assertEqual(data[str(res_id)]["room"], "Board-1")

    def test_conflict_logging(self):
        """Test logging conflicts to file."""
        scheduler_system.schedule_room("Board-1", "09-11")
        scheduler_system.schedule_room("Board-1", "09-11")
        scheduler_system.log_conflicts(self.test_log)

        self.assertTrue(os.path.exists(self.test_log))
        with open(self.test_log, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Board-1 double-booked at 09-11", content)


if __name__ == "__main__":
    unittest.main()
