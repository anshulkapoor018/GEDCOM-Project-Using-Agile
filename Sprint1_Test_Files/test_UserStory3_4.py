from Sprint1_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US03_US04_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    # Run after changing the setUpClass method to testing File -> "US01_US02_testing.ged"
    def test_death_before_birth(self):
        """ Test if Death is before birth """
        self.assertNotEqual(self.errorlog["US03_death_before_birth"], 0)  # There are errors in the gedcom Test file

    def test_marriage_occurs_beforedivorce(self):
        """ Test if Marriage occurs before divorce of spouses, and divorce can only occur after marriage """
        self.assertNotEqual(self.errorlog["US04_MarriageOccursBeforeDivorce"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)