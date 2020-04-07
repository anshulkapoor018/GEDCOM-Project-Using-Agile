from Sprint4_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US28_US29_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()


    def test_DeceasedList(self):
        """ Test list of deceased people """
        g = Gedcom("US28_US29_testing.ged", "n")
        g.analyze_gedcom_file()
        self.assertEqual(g.expiredPeople, ['Laxmi /Kapoor/', 'Shakuntala /Kapoor/', 'Hemant /Arora/', 'Pratap /Kapoor/'])

    
    def test_OrderSiblings(self):
        """Test if siblings list is in order"""
        self.assertNotEqual(self.errorlog["OrderSiblings"], 0)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)