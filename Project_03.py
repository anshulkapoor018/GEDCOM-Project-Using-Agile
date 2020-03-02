import pathlib
import sys
from collections import defaultdict
from prettytable import PrettyTable
import datetime
from datetime import date
import unittest


class TestMarriage(unittest.TestCase):
    def test_divorce(self):
        """ to test if the divorce date is not before marriage date """
        with self.assertRaises(KeyError):
            Gedcom.check_divorce(Gedcom("gedcomData.ged"), "1 JAN 2000", "12 JUN 1999", "test")

    def test_death_date(self):
        """ to test if the death date is not before marriage date """
        with self.assertRaises(KeyError):
            Gedcom.checkMarriageBeforeDeath(Gedcom("gedcomData.ged"), "1 JAN 1930", "12 JUN 2000", "test")


# possible values as global constant Level Wise
VALID_VALUES = {"0": ["INDI", "HEAD", "TRLR", "NOTE", "FAM"],
                "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
                "2": ["DATE"]}


class Gedcom:

    def __init__(self, file):
        self.file = file
        self.directory = pathlib.Path(__file__).parent

        self.output = ""
        self.tempdata = ""
        self.curr_id = ""

        self.individualdata = defaultdict(dict)
        self.familydata = defaultdict(dict)
        self.errorlog = defaultdict(int)

        self.prettytableindividuals = PrettyTable()
        self.prettytablefamily = PrettyTable()

    def analyze_gedcom_file(self):
        """ Function to check if file is valid """
        if self.file.endswith("ged"):
            self.check_gedcom_file(self.open_file())
            self.date_calculation()
            return self.output, self.individualdata, self.familydata
        else:
            return "Can only analyze gedcom files. Enter a file ending with .ged"

    def open_file(self):
        """ Function to try and open the file """
        try:
            with open(self.file, 'r') as ged:
                lines = ged.readlines()
        except FileNotFoundError:
            print("{} Not found in {}".format(self.file, self.directory))
            sys.exit()
        return lines

    def check_gedcom_file(self, read_lines):
        """ Function to read input file line by line and generate output """
        for offset, line in enumerate(read_lines):
            line = line.strip()
            if line == "":  # if last line is reached, return output
                return self.output
            split_words = line.split(" ")
            len_split_words = len(split_words)
            if split_words[0] in ["0", "1", "2"]:
                self.parse_gedcom_file(line, split_words, len_split_words, offset)
            else:
                return "Invalid line on {}".format(line)

    def add_individual_data(self, split_words):
        """ Helper function to add Husband and Wife Data to Individual Data """
        self.individualdata[split_words[1]] = {}
        self.curr_id = split_words[1]

    def add_family_data(self, split_words):
        """ Helper function to add Family Data """
        self.familydata[split_words[1]] = {}
        self.familydata[split_words[1]]["CHIL"] = []
        self.curr_id = split_words[1]

    def add_couple_data(self, split_words):
        """ Helper function to add Husband and Wife Data to Family Data """
        self.familydata[self.curr_id][split_words[1]] = split_words[2]

    def add_children_data(self, split_words):
        """ Helper function to add Children Data to Family Data """
        self.familydata[self.curr_id][split_words[1]].append(split_words[2])

    def add_dates(self, split_words_list):
        """ Helper function to add Dates to Family Data and Individual Data """
        if self.curr_id in self.individualdata:
            self.individualdata[self.curr_id][self.tempdata + split_words_list[1]] = split_words_list[2]
        elif split_words_list[1] == "DATE":
            husband = self.familydata[self.curr_id]["HUSB"]
            wife = self.familydata[self.curr_id]["WIFE"]
            self.individualdata[husband][self.tempdata + split_words_list[1]] = split_words_list[2]
            self.individualdata[wife][self.tempdata + split_words_list[1]] = split_words_list[2]

    def date_calculation(self):
        """ Helper function to Calculate Age and Date with format '%d %b %Y' """
        for key in self.individualdata:
            today = date.today()
            try:
                birthday = self.individualdata[key]["BIRTDATE"]
                born_date = datetime.datetime.strptime(birthday, '%d %b %Y')
            except ValueError:
                print("Invalid date found")
                sys.exit()
            except KeyError:
                print(self.individualdata[key])
                print("Invalid data for {}".format(self.individualdata[key]))
                sys.exit()
            try:
                death_date = self.individualdata[key]["DEATDATE"]
                deathday = self.individualdata[key]["DEATDATE"]
                death_date = datetime.datetime.strptime(deathday, '%d %b %Y')
                alive_status = False
            except KeyError:
                alive_status = True
            self.individualdata[key]["ALIVE"] = alive_status
            if alive_status is True:
                age = today.year - born_date.year
            else:
                age = death_date.year - born_date.year
            self.individualdata[key]["AGE"] = age

            try:
                self.check_divorce(self.individualdata[key]["DIVDATE"],
                                   self.individualdata[key]["DEATDATE"], key)
            except KeyError:
                raise KeyError("Error: divorce can't be after death date for ", key)

            try:
                self.checkMarriageBeforeDeath(self.individualdata[key]["DEATDATE"],self.individualdata[key]["MARRDATE"],
                                              key)
            except KeyError:
                raise KeyError("Error: marriage can't be after death for ", key)

        error = self.prettyTableHelperFunction()
        if error is None:
            error = "No errors found"
        return error, self.errorlog

    def parse_gedcom_file(self, line, split_words, len_split_words, offset):
        """ Helper function to parse gedcom file and extract data """
        if len_split_words > 3:
            split_words[2] += " " + " ".join(split_words[3:])
        process_flow_dict = {"INDI": self.add_individual_data, "FAM": self.add_family_data}
        if split_words[0] == "0":
            if split_words[2] in process_flow_dict:
                process_flow_dict[split_words[2]](split_words)
                return
        process_flow2_dict = {"NOTE": self.donothing, "HUSB": self.add_couple_data, "WIFE": self.add_couple_data,
                              "CHIL": self.add_children_data, "FAM": self.donothing, "INDI": self.donothing}

        try:
            if split_words[1] not in VALID_VALUES[split_words[0]]:
                if len_split_words < 3:  # if no, add N after tag
                    self.tempdata = split_words[1]
            else:  # if yes add Y after tag
                if len_split_words < 3:
                    self.tempdata = split_words[1]
                else:
                    if split_words[1] in process_flow2_dict:
                        process_flow2_dict[split_words[1]](split_words)
                        return
                    if split_words[0] == "2":
                        self.add_dates(split_words)
                        return
                    else:
                        self.individualdata[self.curr_id][split_words[1]] = split_words[2]
        except KeyError:  # Throw error if Level is invalid
            print("Invalid line found on {}".format(offset + 1))

    def prettyTableHelperFunction(self):

        self.prettytableindividuals.field_names = ["ID", "NAME", "GENDER", "BIRTH DATE",
                                                   "AGE", "ALIVE", "DEATH", "CHILD", "SPOUSE"]

        for key in sorted(self.individualdata.keys()):
            value = self.individualdata[key]
            name = value["NAME"]
            gender = value["SEX"]
            birthdate = value["BIRTDATE"]
            age = value["AGE"]
            alive = value["ALIVE"]

            try:
                death = value["DEATDATE"]
            except KeyError:
                death = "NA"
            try:
                fam_id = value["FAMS"]
                if fam_id == {}:
                    raise KeyError
                child = self.familydata[fam_id]["CHIL"]

                self.individualdata[key]["CHILD"] = child
                for c in child:

                    if gender == "M":
                        self.individualdata[c]["father"] = key
                    if gender == "F":
                        self.individualdata[c]["mather"] = key

            except KeyError:
                child = "NA"
                self.individualdata[key]["CHILD"] = child
            try:
                fam_id = value["FAMS"]
                if fam_id == {}:
                    raise KeyError
                if gender == "M":
                    spouse = self.familydata[fam_id]["WIFE"]
                    self.individualdata[key]["SPOUSE"] = spouse
                else:
                    spouse = self.familydata[fam_id]["HUSB"]
                    self.individualdata[key]["SPOUSE"] = spouse
            except KeyError:
                spouse = "NA"

            self.prettytableindividuals.add_row([key, name, gender, birthdate, age, alive, death, child, spouse])

        self.prettytablefamily.field_names = ["ID", "MARRIAGE DATE", "DIVORCE DATE", "HUSBAND ID",
                                              "HUSBAND NAME", "WIFE ID", "WIFE NAME", "CHILDREN"]

        for key in sorted(self.familydata.keys()):

            value = self.familydata[key]

            husband_id = value["HUSB"]
            wife_id = value["WIFE"]
            children = value["CHIL"]

            husband_name = self.individualdata[husband_id]["NAME"]

            try:
                marriage = self.individualdata[husband_id]["MARRDATE"]
            except KeyError:
                return "No Marriage date found"

            wife_name = self.individualdata[wife_id]["NAME"]

            try:
                divorce = self.individualdata[husband_id]["DIVDATE"]
            except KeyError:
                divorce = "NA"

            try:
                child = value["CHIL"]
            except KeyError:
                child = "NA"
            self.prettytablefamily.add_row(
                [key, marriage, divorce, husband_id, husband_name, wife_id, wife_name, child])

    def check_divorce(self, divorce, death, key):
        """ if the divorce is after death, raise KeyError """
        div_date = datetime.datetime.strptime(divorce, '%d %b %Y')
        death_date = datetime.datetime.strptime(death, '%d %b %Y')
        result = death_date - div_date

        if result.days < 0:
            self.errorlog[key] += 1
            raise KeyError

    def checkMarriageBeforeDeath(self, death_date, marriage, key):
        """ if the death is before marriage, raise KeyError """
        death_date = datetime.datetime.strptime(death_date, '%d %b %Y')
        marr_date = datetime.datetime.strptime(marriage, '%d %b %Y')
        result = death_date - marr_date

        if result.days < 0:
            self.errorlog[key] += 1
            raise KeyError

    def donothing(self, nothing):
        pass


def main():
    file_name = input("Enter file name: ")
    g = Gedcom(file_name)
    output, userData, familyData = g.analyze_gedcom_file()
    print(g.prettytableindividuals)
    print(g.prettytablefamily)


if __name__ == '__main__':
    unittest.main(exit=False, verbosity=2)
    main()
