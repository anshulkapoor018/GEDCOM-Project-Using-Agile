from Sprint3_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US23_US31_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()

    def test_uniquenamebirthdate(self):
        self.assertNotEqual(self.errorlog["UniqueNameBirthDate"], 0)

    def test_listingSingles(self):
        """ To Test US31_Include_individual_ages while listing """
        print("------------- Testing the listing of Singles in Gedcom File -------------")
        g = Gedcom("../gedcomData.ged", "y")
        print(g.analyze_gedcom_file())
        print(g.singlesList)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)