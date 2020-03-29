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




if __name__ == '__main__':
    # note: there is no main(). Only test cases here
    unittest.main(exit=False, verbosity=2)