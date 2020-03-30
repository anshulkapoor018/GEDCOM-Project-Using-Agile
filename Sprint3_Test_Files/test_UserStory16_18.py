from Sprint3_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US16_US18_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_MaleLastNames(self):
        """ To Test if Last Name of All the males in Family are same """
        self.assertNotEqual(self.errorlog["US16_MaleLastNames"], 0)

    def test_SiblingsMarriage(self):
        """ To Test if Siblings are married or not """
        self.assertNotEqual(self.errorlog["US18_SiblingMarriageError"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)