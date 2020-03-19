from Sprint1_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US01_US02_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    # Run after changing the setUpClass method to testing File -> "US01_US02_testing.ged"
    def test_date_before_current_date(self):
        """ Test if Dates (birth, marriage, divorce, death) should not be after the current date """
        self.assertNotEqual(self.errorlog["US01_DateAfterCurrent"], 0)  # There are errors in the gedcom Test file

    def test_marriage_before_birth_date(self):
        """ Test if marriage date is before birth date """
        self.assertNotEqual(self.errorlog["US02_BirthBeforeMarriage"], 0)  # There are errors in the gedcom Test file


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)