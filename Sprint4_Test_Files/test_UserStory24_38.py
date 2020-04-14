from Sprint4_Main import Gedcom
import unittest


class TestGedcom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Set up objects with filenames """
        cls.x = Gedcom("US24_US38_testing.ged", "n")
        cls.errorlog = cls.x.analyze_gedcom_file()
        cls.recentDeceased = cls.x.recentDeceased
        cls.upcomingBirthdayList = cls.x.BirthdayList

    def test_RecentBirthdayList(self):
        """ Test list of recent birthday """
        self.assertEqual(self.upcomingBirthdayList, ['Nishi /Dhawan/'])
        self.assertNotEqual(self.upcomingBirthdayList, ['Anshul /Kapoor/'])

    def test_uniqueFamily(self):
        """Test Unique Families by spouses"""
        self.assertNotEqual(self.errorlog["US24_UniqueFamily"], 0)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)