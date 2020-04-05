from Sprint3_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US26_US27_testing.ged", "y")
        cls.errorlog = cls.x.analyze_gedcom_file()

    def test_Corresponding_entries(self):
        """ To test if the individual and family records is consistent with each other """
        self.assertNotEqual(self.errorlog["US26_Corresponding_entries"], 0)

    def test_Include_individual_ages(self):
        """ To Test US27_Include_individual_ages while listing """
        print("------------- Testing of Include person's current age when listing individuals done -------------")
        g = Gedcom("../gedcomData.ged", "y")
        g.analyze_gedcom_file()
        self.assertEqual(g.individualdata["I1"]['AGE'], 26)
        self.assertEqual(g.individualdata["I2"]['AGE'], 61)
        self.assertEqual(g.individualdata["I17"]['AGE'], 78)
        self.assertNotEqual(g.individualdata["I15"]['AGE'], 16)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)
