from Sprint2_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US13_US14_testing.ged")
        cls.errorlog = cls.x.analyze_gedcom_file()

    def test_siblings_spacing(self):
        """ to test if siblings have valid spacing """

        self.assertNotEqual(self.errorlog["US13 Siblings spacing:"], 0)

    def test_multiple_births(self):
        """ to test number of twins is not more than 5 """

        self.assertNotEqual(self.errorlog["US14 Multiple births <= 5:"], 0)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)