from Sprint2_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US15_US17_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_descendantmarryparent(self):
        """ To Test if Parents should not marry any of their descendants """
        self.assertNotEqual(self.errorlog["DescendantChildrenMarriage"], 0)

    def test_siblingsgreaterthan15(self):
        """ To Test if There should be fewer than 15 siblings in a family """
        self.assertNotEqual(self.errorlog["SiblingGreaterThan15"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)