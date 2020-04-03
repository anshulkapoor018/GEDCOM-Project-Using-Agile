from Sprint3_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US26_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()
        cls.y = Gedcom("US27_testing.ged", "n")
        cls.errorlog = cls.y.analyze_gedcom_file()

    def test_Corresponding_entries(self):
        """ To test if the individual and family records is consistent with each other """
        self.assertNotEqual(self.errorlog["US26_Corresponding_entries"], 0)

    def test_Include_individual_ages(self):
        """ To Test US27_Include_individual_ages """
        self.assertNotEqual(self.errorlog["US27_Include_individual_ages"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)
