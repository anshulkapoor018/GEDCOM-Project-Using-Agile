import pathlib
import unittest

import sys
from collections import defaultdict
from prettytable import PrettyTable
import datetime
from datetime import date

# define possible values as global constant
VALID_VALUES = {"0": ["INDI", "HEAD", "TRLR", "NOTE", "FAM"],
                "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
                "2": ["DATE"]}


class Gedcom:

    def __init__(self, file, pretty):

        self.file = file
        self.directory = pathlib.Path(__file__).parent
        self.output = ""
        self.userdata = defaultdict(dict)
        self.familydata = defaultdict(dict)
        self.tempdata = ""
        self.curr_id = ""
        self.samenameandbirthdate = []
        self.ptUsers = PrettyTable()
        self.ptFamily = PrettyTable()
        self.errorlog = defaultdict(int)
        if pretty.lower() == "y":
            self.bool_to_print = True
        elif pretty.lower() == "n":
            self.bool_to_print = False
        else:
            print("Invalid input for pretty table argument")

    def analyze(self):
        """
        Function to check if file is valid
        """

        if self.file.endswith("ged"):
            self.check_file(self.open_file())
            self.calc_data()
            return self.output, self.userdata, self.familydata
        else:
            return "Can only analyze gedcom files. Enter a file ending with .ged"

    def open_file(self):
        """
        Function to try and open the file
        :return: Returns lines in the file if file is valid
        """
        try:
            with open(self.file, 'r') as ged:
                lines = ged.readlines()
        except FileNotFoundError:
            print("{} Not found in {}".format(self.file, self.directory))
            sys.exit()
        return lines

    def check_file(self, read_lines):
        """
        Function to read input file line by line and generate output
        :param read_lines: list
        :return: output as string
        """

        for offset, line in enumerate(read_lines):
            line = line.strip()
            if line == "":  # if last line is reached, return output
                return self.output
            split_words = line.split(" ")
            len_split_words = len(split_words)
            if split_words[0] in ["0", "1", "2"]:
                self.parse_file(line, split_words, len_split_words, offset)
            else:
                return "Invalid line on {}".format(line)

    def parse_file(self, line, split_words, len_split_words, offset):

        if len_split_words > 3:  # if there is a big name or date, append it to a single value in list
            split_words[2] += " " + " ".join(split_words[3:])
        process_flow_dict = {"INDI": self.append2userdata, "FAM": self.append2familydata}
        if split_words[0] == "0":
            if split_words[2] in process_flow_dict:
                process_flow_dict[split_words[2]](split_words)
                return
        process_flow2_dict = {"NOTE": self.donothing, "HUSB": self.appendHusbWifedata, "WIFE": self.appendHusbWifedata,
                              "CHIL": self.appendChilddata, "FAM": self.donothing, "INDI": self.donothing}

        try:
            if split_words[1] not in VALID_VALUES[
                split_words[0]]:  # check if splitwords[1] which is the tag value is in the global dictionary
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
                        self.appendDates(split_words)
                        return
                    else:
                        self.userdata[self.curr_id][split_words[1]] = split_words[2]
        except KeyError:  # if invalid level value, throw eror
            print("Invalid line found on {}".format(offset + 1))

    def append2userdata(self, split_words):

        if self.userdata.__contains__(split_words[1]):
            print("ERROR: US22 INDIVIDUAL {} has a repetitive ID".format(split_words[1]))
            self.errorlog["RepetitiveID"] += 1

        self.userdata[split_words[1]] = {}
        self.curr_id = split_words[1]

    def append2familydata(self, split_words):

        if self.familydata.__contains__(split_words[1]):
            print("ERROR: US 08 FAMILY {} has a repetitive ID".format(split_words[1]))
            self.errorlog["RepetitiveID"] += 1

        self.familydata[split_words[1]] = {}
        self.familydata[split_words[1]]["CHIL"] = []
        self.curr_id = split_words[1]

    def appendHusbWifedata(self, split_words):
        self.familydata[self.curr_id][split_words[1]] = split_words[2]

    def appendChilddata(self, split_words):
        self.familydata[self.curr_id][split_words[1]].append(split_words[2])

    def appendDates(self, split_words):

        if self.curr_id in self.userdata:
            if self.tempdata + split_words[1] == "MARRDATE":
                if self.userdata[self.curr_id].__contains__("MARRDATE"):
                    try:
                        self.userdata[self.curr_id]["DIVDATE"]
                    except KeyError:
                        print("ERROR: US11 INDIVIDUAL {} HAS DONE BIGAMY".format(self.curr_id))
                        self.errorlog["Bigamy"] += 1

            self.userdata[self.curr_id][self.tempdata + split_words[1]] = split_words[2]
        elif split_words[1] == "DATE":
            husband = self.familydata[self.curr_id]["HUSB"]
            wife = self.familydata[self.curr_id]["WIFE"]
            self.userdata[husband][self.tempdata + split_words[1]] = split_words[2]
            self.userdata[wife][self.tempdata + split_words[1]] = split_words[2]

    def donothing(self, nothing):
        pass

    def calc_data(self):
        for key in self.userdata:
            today = date.today()
            try:
                birthday = self.userdata[key]["BIRTDATE"]
                born_date = datetime.datetime.strptime(birthday, '%d %b %Y')
            except ValueError:
                print("Invalid date found")
                sys.exit()
            except KeyError:
                print(self.userdata[key])
                print("Invalid data for {}".format(self.userdata[key]))
                sys.exit()
            try:
                death_date = self.userdata[key]["DEATDATE"]
                deathday = self.userdata[key]["DEATDATE"]
                death_date = datetime.datetime.strptime(deathday, '%d %b %Y')
                alive_status = False
            except KeyError:
                alive_status = True
            self.userdata[key]["ALIVE"] = alive_status
            if alive_status is True:
                age = today.year - born_date.year
            else:
                age = death_date.year - born_date.year
            self.userdata[key]["AGE"] = age

        error = self.prettyTableHelperFunction()
        if error is None:
            error = "No errors found"
        return error, self.errorlog

    def prettyTableHelperFunction(self):

        self.ptUsers.field_names = ["ID", "NAME", "GENDER", "BIRTH DATE",
                                    "AGE", "ALIVE", "DEATH", "CHILD", "SPOUSE"]

        for key in sorted(self.userdata.keys()):

            value = self.userdata[key]
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

                self.userdata[key]["CHILD"] = child
                for c in child:

                    if gender == "M":
                        self.userdata[c]["father"] = key
                    if gender == "F":
                        self.userdata[c]["mather"] = key

            except KeyError:
                child = "NA"
                self.userdata[key]["CHILD"] = child
            try:
                fam_id = value["FAMS"]
                if fam_id == {}:
                    raise KeyError
                if gender == "M":
                    spouse = self.familydata[fam_id]["WIFE"]
                    self.userdata[key]["SPOUSE"] = spouse
                else:
                    spouse = self.familydata[fam_id]["HUSB"]
                    self.userdata[key]["SPOUSE"] = spouse
            except KeyError:
                spouse = "NA"

            try:
                marriage = value["MARRDATE"]
            except KeyError:
                marriage = "NA"

            self.ptUsers.add_row([key, name, gender, birthdate, age, alive, death, child, spouse])

        # print(self.ptUsers)

        self.ptFamily.field_names = ["ID", "MARRIAGE DATE", "DIVORCE DATE", "HUSBAND ID",
                                     "HUSBAND NAME", "WIFE ID","WIFE NAME", "CHILDREN"]

        for key in sorted(self.familydata.keys()):

            value = self.familydata[key]

            husband_id = value["HUSB"]
            wife_id = value["WIFE"]
            children = value["CHIL"]

            husband_name = self.userdata[husband_id]["NAME"]

            try:
                marriage = self.userdata[husband_id]["MARRDATE"]
            except KeyError:
                return "No Marriage date found"

            wife_name = self.userdata[wife_id]["NAME"]

            try:
                divorce = self.userdata[husband_id]["DIVDATE"]

            except KeyError:
                divorce = "NA"

            try:
                child = value["CHIL"]
            except KeyError:
                child = "NA"
            self.ptFamily.add_row([key, marriage, divorce, husband_id, husband_name, wife_id, wife_name, child])
        # print(self.ptFamily)


def main():
    # file = input("Enter file name: \n")
    # print(file)
    g = Gedcom('gedcomData.ged', 'y')
    output, userData, familyData = g.analyze()
    print(g.ptUsers)
    print(g.ptFamily)


if __name__ == '__main__':
    main()
