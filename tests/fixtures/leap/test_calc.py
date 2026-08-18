import unittest

from calc import days_in_february, is_leap


class LeapTests(unittest.TestCase):
    def test_2024_is_leap(self):
        self.assertTrue(is_leap(2024))

    def test_2023_is_not_leap(self):
        self.assertFalse(is_leap(2023))

    def test_february_2024_has_29_days(self):
        self.assertEqual(days_in_february(2024), 29)


if __name__ == "__main__":
    unittest.main()
