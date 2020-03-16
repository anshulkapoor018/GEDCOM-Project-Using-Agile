from Sprint2_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US08_US09_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    # Run after changing the setUpClass method to testing File -> "US01_US02_testing.ged"
    def test_birthBeforeMarriageOfParents(self):
        """ """
        self.assertNotEqual(self.errorlog["US08_BirthBeforeMarriageOfParents"], 0)  # There are errors in the gedcom Test file

    def test_birthBeforeDeathOfParents(self):
        """  """
        self.assertNotEqual(self.errorlog["US09_BirthBeforeDeathOfParents"], 0)  # There are errors in the gedcom Test file


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)