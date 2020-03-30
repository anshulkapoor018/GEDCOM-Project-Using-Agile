from Sprint3_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US16_US18_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_MaleLastNames(self):
        """ To Test if Parents should not marry any of their descendants """
        self.assertNotEqual(self.errorlog["US16_MaleLastNames"], 0)

    # def test_RepetitiveID(self):
    #     """ To Test if There should be fewer than 15 siblings in a family """
    #     self.assertNotEqual(self.errorlog["RepetitiveID"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)