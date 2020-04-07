from Sprint4_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US19_US34_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()
        cls.recentDeceased = cls.x.recentDeceased

    def test_RecentDeceasedList(self):
        """ Test list of recently deceased people """
        self.assertEqual(self.recentDeceased, ['Hemant /Arora/'])

    def test_CoupleAgeDifference(self):
        """Test if Couple has very large Age difference"""
        self.assertNotEqual(self.errorlog["US34_AgeDifference"], 0)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)