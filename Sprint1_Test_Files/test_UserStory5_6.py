from Sprint1_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US05_US06_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    # Run after changing the setUpClass method to testing File -> "US01_US02_testing.ged"
    def test_divorce_before_death(self):
        """ to test if the divorce date is not before marriage date """
        # with self.assertRaises(KeyError):
        #     Gedcom.check_divorce(Gedcom("gedcomData.ged"), "1 JAN 2000", "12 JUN 1999", "test")
        self.assertNotEqual(self.errorlog["US06_check_divorce"], 0)

    def test_marriage_before_death_date(self):
        """ to test if the death date is not before marriage date """
        # with self.assertRaises(KeyError):
        #     Gedcom.checkMarriageBeforeDeath(Gedcom("gedcomData.ged"), "1 JAN 1930", "12 JUN 2000", "test")
        self.assertNotEqual(self.errorlog["US05_checkMarriageBeforeDeath"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)