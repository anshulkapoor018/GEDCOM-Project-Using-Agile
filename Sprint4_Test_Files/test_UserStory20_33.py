from Sprint4_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US20_US33_testing.ged", "y")
        cls.errorlog = cls.x.analyze_gedcom_file()

    def test_US20_Aunts_and_Uncles(self):
        """ Check: Aunts and uncles should not marry their nieces or nephews """
        self.assertNotEqual(self.errorlog["US20_Aunts_and_Uncles"], 0)

    def test_US33_List_orphans(self):
        """ Check: List all orphaned children (both parents dead and child < 18 years old) """
        self.assertNotEqual(self.errorlog["US33_List_orphans"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)
