from Sprint1_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US07_US08_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    # Run after changing the setUpClass method to testing File -> "US01_US02_testing.ged"
    def test_age_150(self):
        """ Test if ALIVE AND OLDER THAN 150 YEARDS """
        self.assertNotEqual(self.errorlog["US07_AgeLessOneFifty"], 0)  # There are errors in the gedcom Test file

    def test_married_before_14(self):
        """ Test if married only after 14 years of age """
        self.assertNotEqual(self.errorlog["US10_MarriageBefore14"], 0)  # There are errors in the gedcom Test file


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)