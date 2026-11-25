import unittest

from eps_tools.packed_angle_word import decode, encode


class TestPackedAngleWord(unittest.TestCase):
    def test_wire_examples(self):
        # The EPS must be able to see mode 1 even at an idle target of zero.
        for angle, mode, expected in (
            (0, 0, "0000"),
            (0, 1, "0001"),
            (1, 1, "0005"),
            (-1, 1, "fffd"),
            (-8192, 1, "8001"),
            (8191, 1, "7ffd"),
        ):
            field = bytes.fromhex(expected)
            self.assertEqual(encode(angle, mode), field)
            self.assertEqual(decode(field), (angle, mode))

    def test_round_trip_all_angles(self):
        for angle in range(-8192, 8192):
            for mode in (0, 1):
                self.assertEqual(decode(encode(angle, mode)), (angle, mode))

    def test_reject_out_of_range_fields(self):
        for angle in (-8193, 8192):
            with self.assertRaisesRegex(ValueError, "angle must be"):
                encode(angle, 1)
        for mode in (2, 3):
            with self.assertRaisesRegex(ValueError, "reserved mode"):
                encode(0, mode)
            with self.assertRaisesRegex(ValueError, "reserved mode"):
                decode(bytes((0, mode)))
        for field in (b"", b"\x00", b"\x00\x00\x00"):
            with self.assertRaisesRegex(ValueError, "two-byte"):
                decode(field)
