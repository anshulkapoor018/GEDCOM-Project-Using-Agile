import unittest
from Project_03 import Gedcom


class TestMarriage(unittest.TestCase):
    def test_divorce(self):
        """ to test if the divorce date is not before marriage date """
        with self.assertRaises(KeyError):
            Gedcom.check_divorce(Gedcom("US05_US06_testing.ged"), "1 JAN 2000", "12 JUN 1999", "test")

    def test_death_date(self):
        """ to test if the death date is not before marriage date """
        with self.assertRaises(KeyError):
            Gedcom.checkMarriageBeforeDeath(Gedcom("US05_US06_testing.ged"), "1 JAN 1930", "12 JUN 2000", "test")


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
