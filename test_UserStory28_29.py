from Sprint4_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US28_US29_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_DeceasedList(self):
        g = Gedcom("US28_US29_testing.ged", "y")
        g.analyze_gedcom_file()
        self.assertEqual(g.expiredPeople, ['Laxmi /Kapoor/', 'Shakuntala /Kapoor/', 'Hemant /Arora/', 'Pratap /Kapoor/'])

    # def test_RepetitiveID(self):
    #     """ To Test if There should be fewer than 15 siblings in a family """
    #     self.assertNotEqual(self.errorlog["RepetitiveID"], 0)


if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)