from Sprint2_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US11_US12_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_bigamy(self):
        """ Test if there is Bigamy """
        self.assertNotEqual(self.errorlog["Bigamy"], 0)

    def test_parentstooold(self):
        """ Test if parents too old """
        self.assertNotEqual(self.errorlog["ParentsTooOld"], 0)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)