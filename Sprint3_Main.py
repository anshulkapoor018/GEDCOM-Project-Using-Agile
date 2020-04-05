import pathlib
import sys
from collections import defaultdict
from prettytable import PrettyTable
import datetime
from datetime import date

# possible values as global constant Level Wise
VALID_VALUES = {"0": ["INDI", "HEAD", "TRLR", "NOTE", "FAM"],
                "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
                "2": ["DATE"]}


class Gedcom:

    def __init__(self, file, pretty):
        self.file = file
        self.directory = pathlib.Path(__file__).parent

        self.output = ""
        self.tempdata = ""
        self.curr_id = ""

        self.samenameandbirthdate = []
        self.individualdata = defaultdict(dict)
        self.familydata = defaultdict(dict)
        self.errorLog = defaultdict(int)
        self.singlesList = []

        self.prettytableindividuals = PrettyTable()
        self.prettytablefamily = PrettyTable()
        if pretty.lower() == "y":
            self.bool_to_print = True
        elif pretty.lower() == "n":
            self.bool_to_print = False
        else:
            print("Invalid input for pretty table argument")

    def analyze_gedcom_file(self):
        """ Function to check if file is valid """
        if self.file.endswith("ged"):
            self.check_gedcom_file(self.open_file())
            # return self.output, self.individualdata, self.familydata
            errorLog = self.date_calculation()
            return errorLog
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

        if self.individualdata.__contains__(split_words[1]):
            print("ERROR: US22 INDIVIDUAL {} has a repetitive ID".format(split_words[1]))
            self.errorLog["RepetitiveID"] += 1

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
            if self.tempdata + split_words_list[1] == "MARRDATE":
                if self.individualdata[self.curr_id].__contains__("MARRDATE"):
                    try:
                        self.individualdata[self.curr_id]["DIVDATE"]
                    except KeyError:
                        print("ERROR: US11 INDIVIDUAL {} HAS DONE BIGAMY".format(self.curr_id))
                        self.errorLog["Bigamy"] += 1

            self.individualdata[self.curr_id][self.tempdata + split_words_list[1]] = split_words_list[2]

        elif split_words_list[1] == "DATE":
            husband = self.familydata[self.curr_id]["HUSB"]
            wife = self.familydata[self.curr_id]["WIFE"]
            self.individualdata[husband][self.tempdata + split_words_list[1]] = split_words_list[2]
            self.individualdata[wife][self.tempdata + split_words_list[1]] = split_words_list[2]

    def date_calculation(self):
        """ Helper function to Calculate Age and Date with format '%d %b %Y' """
        for key in self.individualdata:
            if "DEATDATE" not in self.individualdata[key].keys():
                self.individualdata[key]["DEATDATE"] = "NA"
                alive_status = True
            if "MARRDATE" not in self.individualdata[key].keys():
                self.individualdata[key]["MARRDATE"] = "NA"
            if "DIVDATE" not in self.individualdata[key].keys():
                self.individualdata[key]["DIVDATE"] = "NA"

            today = date.today()
            try:  # To check if birthdate is not in future
                birthday = self.individualdata[key]["BIRTDATE"]
                born_date = datetime.datetime.strptime(birthday, '%d %b %Y')
                if born_date > datetime.datetime.now():
                    print("ERROR: US01 INDIVIDUAL () {} has Birthdate in future".format(key, self.individualdata[key][
                        "NAME"]))
                    self.errorLog["US01_DateAfterCurrent"] += 1
            except ValueError:
                print("Invalid birthdate Value for {}".format(self.individualdata[key]["NAME"]))
                sys.exit()
            except KeyError:
                self.errorLog["US27_Include_individual_ages"] += 1
                print("Invalid data for {}".format(self.individualdata[key]["NAME"]))
                sys.exit()

            if self.individualdata[key]["DEATDATE"] != "NA":
                try:  # To check if deathDate is not in future
                    death_date = self.individualdata[key]["DEATDATE"]
                    deathday = self.individualdata[key]["DEATDATE"]
                    death_date = datetime.datetime.strptime(deathday, '%d %b %Y')
                    if death_date > datetime.datetime.now():
                        print("ERROR: US01 INDIVIDUAL () {} has Death Date in future".format(key,
                                                                                             self.individualdata[key][
                                                                                                 "NAME"]))
                        self.errorLog["US01_DateAfterCurrent"] += 1
                    alive_status = False
                except ValueError:
                    print("Invalid death date Value for {}".format(self.individualdata[key]["NAME"]))
                    sys.exit()
                except KeyError:
                    alive_status = True

            self.individualdata[key]["ALIVE"] = alive_status
            if alive_status is True:
                age = today.year - born_date.year
            else:
                age = death_date.year - born_date.year
            self.individualdata[key]["AGE"] = age

            try:  # if a person is alive and older than 150 years
                if alive_status is True and age > 150:
                    print("ERROR: US07 INDIVIDUAL () {} has AGE greater than 150 ".format(key, self.individualdata[key][
                        "NAME"]))
                    self.errorLog["US07_AgeLessOneFifty"] += 1
            except ValueError:
                print("Invalid Age Value for {}".format(self.individualdata[key]["NAME"]))
                sys.exit()
            except KeyError:
                print("Invalid data for {}".format(self.individualdata[key]["NAME"]))
                sys.exit()

            birthday = self.individualdata[key]["BIRTDATE"]
            try:  # check if marriage before 14
                marriageday = self.individualdata[key]["MARRDATE"]
            except KeyError:
                marriageDate = "NA"

            if marriageday != "NA" and (int(marriageday.split()[2]) - int(birthday.split()[2])) < 14:
                print("ERROR: US10 INDIVIDUAL () {} has married before the age of 14 ".format(key,
                                                                                              self.individualdata[key][
                                                                                                  "NAME"]))
                self.errorLog["US10_MarriageBefore14"] += 1

            try:
                if self.individualdata[key]["MARRDATE"] != "NA" and self.individualdata[key]["DEATDATE"] != "NA":
                    self.checkMarriageBeforeDeath(self.individualdata[key]["DEATDATE"],
                                                  self.individualdata[key]["MARRDATE"], key)
            except KeyError:
                print("ERROR: US05: marriage can't be after death for {}".format(self.individualdata[key]["NAME"]))

            try:
                if self.individualdata[key]["DIVDATE"] != "NA" and self.individualdata[key]["DEATDATE"] != "NA":
                    self.check_divorce(self.individualdata[key]["DIVDATE"], self.individualdata[key]["DEATDATE"], key)
            except KeyError:
                print("ERROR: US06: divorce can't be after death date for  {}".format(self.individualdata[key]["NAME"]))

            if self.individualdata[key]["MARRDATE"] != "NA":
                try:  # To check if marriage Date is not in future
                    marriageDate = self.individualdata[key]["MARRDATE"]
                    marr_date = datetime.datetime.strptime(marriageDate, '%d %b %Y')
                    if marr_date > datetime.datetime.now():
                        print("ERROR: US01 INDIVIDUAL {} has marriage Date in future".format(key,
                                                                                             self.individualdata[key][
                                                                                                 "NAME"]))
                        self.errorLog["US01_DateAfterCurrent"] += 1
                    if marr_date < datetime.datetime.strptime(self.individualdata[key]["BIRTDATE"], '%d %b %Y'):
                        print("ERROR: US02 INDIVIDUAL {} has marriage Date before Birth".format(key,
                                                                                                self.individualdata[
                                                                                                    key]["NAME"]))
                        self.errorLog["US02_BirthBeforeMarriage"] += 1
                except ValueError:
                    print("Invalid marriage date Value for {}".format(self.individualdata[key]["NAME"]))
                    sys.exit()
                except KeyError:
                    print("Invalid data for {}".format(self.individualdata[key]["NAME"]))
                    sys.exit()

            if self.individualdata[key]["DEATDATE"] != "NA":
                try:
                    death_date = self.individualdata[key]["DEATDATE"]
                    deathday = self.individualdata[key]["DEATDATE"]
                    death_date = datetime.datetime.strptime(deathday, '%d %b %Y')
                    birthday = self.individualdata[key]["BIRTDATE"]
                    born_date = datetime.datetime.strptime(birthday, '%d %b %Y')
                    if death_date < born_date:
                        print("ERROR: US03 INDIVIDUAL () {} has Death date Date before Birth date".format(key,
                                                                                                          self.individualdata[
                                                                                                              key][
                                                                                                              "NAME"]))
                        self.errorLog["US03_death_before_birth"] += 1
                    alive_status = False
                except KeyError:
                    alive_status = True

            if self.individualdata[key]["DIVDATE"] != "NA":
                try:  # To check if divorce Date is not in future
                    divorceDate = self.individualdata[key]["DIVDATE"]
                    div_date = datetime.datetime.strptime(divorceDate, '%d %b %Y')
                    if div_date > datetime.datetime.now():
                        print("ERROR: US01 INDIVIDUAL () {} has divorce Date in future".format(key,
                                                                                               self.individualdata[key][
                                                                                                   "NAME"]))
                        self.errorLog["US01_DateAfterCurrent"] += 1
                except ValueError:
                    print("Invalid divorce date Value for {}".format(self.individualdata[key]["NAME"]))
                    sys.exit()
                except KeyError:
                    print("Invalid data for {}".format(self.individualdata[key]["NAME"]))
                    sys.exit()

        self.prettyTableHelperFunction()
        return self.errorLog

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
        single_list = []
        married_list = []
        test_single = []
        test_married = []
        deceased_list = []
        test_deceased = []

        for key in sorted(self.individualdata.keys()):
            value = self.individualdata[key]
            name = value["NAME"]
            gender = value["SEX"]
            birthdate = value["BIRTDATE"]
            age = value["AGE"]
            alive = value["ALIVE"]

            if name + birthdate in self.samenameandbirthdate:
                print("ERROR: US23 INDIVIDUAL {} {} does not have a unique name and birth date".format(key, name))
                self.errorLog["UniqueNameBirthDate"] += 1
            else:
                self.samenameandbirthdate.append(name + birthdate)

            # try:
            #     value["MARRDATE"]
            #     married_list.append(value["NAME"])
            #     test_married.append(value["NAME"])

            # except KeyError:
            #     single_list.append(value["NAME"])
            #     test_single.append(value["NAME"])

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

            if age > 30 and spouse == "NA" and alive is True:
                """ US_31 Creating a list of all individuals who are aged more than 30 and not married """
                self.singlesList.append(name)

            self.prettytableindividuals.add_row([key, name, gender, birthdate, age, alive, death, child, spouse])

        # if self.bool_to_print:
        #     # print(self.prettytableindividuals)

        #     print("DISPLAY US31 LIST OF SINGLES: {}".format(single_list))

        self.prettytablefamily.field_names = ["ID", "MARRIAGE DATE", "DIVORCE DATE", "HUSBAND ID",
                                              "HUSBAND NAME", "WIFE ID", "WIFE NAME", "CHILDREN"]

        multiple_births = []
        test_multiple = []
        age_list = []
        test_order = []

        US26_IDs = defaultdict(int)

        for key in sorted(self.familydata.keys()):

            value = self.familydata[key]

            husband_individiual_id = value["HUSB"]
            wife_individiual_id = value["WIFE"]
            children = value["CHIL"]

            if abs(datetime.datetime.strptime(self.individualdata[husband_individiual_id]["BIRTDATE"],
                                              '%d %b %Y') - datetime.datetime.strptime(
                self.individualdata[wife_individiual_id]["BIRTDATE"], '%d %b %Y')).days > 5475:
                print("ERROR: US17 FAMILY {} has marriage between descendants and their children".format(key))
                self.errorLog["DescendantChildrenMarriage"] += 1

            if len(children) > 15:
                print("ERROR: US15 FAMILY {} more than 15 siblings".format(key))
                self.errorLog["SiblingGreaterThan15"] += 1

            for i in children:
                age_list.append(self.individualdata[i]["AGE"])
                test_order.append(self.individualdata[i]["AGE"])
                if len(children) >= 2:
                    multiple_births.append(i)
                    test_multiple.append(i)

            try:
                marriage = self.individualdata[husband_individiual_id]["MARRDATE"]
            except KeyError:
                return "No Marriage date found"

            husband_name = self.individualdata[husband_individiual_id]["NAME"]
            husband_firstname, husband_lastname = husband_name.split()
            wife_name = self.individualdata[wife_individiual_id]["NAME"]
            wife_firstname, wife_lastname = wife_name.split()

            try:
                divorce = self.individualdata[husband_individiual_id]["DIVDATE"]
                div_husband = self.individualdata[wife_individiual_id]["DIVDATE"]
                div_wife = self.individualdata[wife_individiual_id]["DIVDATE"]
            except KeyError:
                divorce = "NA"
                div_husband = "NA"
                div_wife = "NA"

            for child in children:
                c_birthday = datetime.datetime.strptime(self.individualdata[child]["BIRTDATE"], '%d %b %Y')
                child_name = self.individualdata[child]["NAME"]
                child_firstname, child_lastname = child_name.split()

                if abs(datetime.datetime.strptime(self.individualdata[husband_individiual_id]["BIRTDATE"],
                                                  '%d %b %Y') - datetime.datetime.strptime(
                    self.individualdata[child]["BIRTDATE"], '%d %b %Y')).days > 29200:
                    print("ERROR: US12 FAMILY {} Parents are too old".format(key))
                self.errorLog["ParentsTooOld"] += 1

                if self.individualdata[husband_individiual_id]["MARRDATE"] != "NA":
                    c_Father_MarriageDate = datetime.datetime.strptime(
                        self.individualdata[husband_individiual_id]["MARRDATE"], '%d %b %Y')
                    try:
                        if c_birthday < c_Father_MarriageDate:
                            print(
                                "ERROR: US08 Family {} has Child {} with Birth date '{}' who was born before parents marriage '{}'"
                                    .format(key, child_firstname, self.individualdata[child]["BIRTDATE"],
                                            self.individualdata[husband_individiual_id]["MARRDATE"]))
                            self.errorLog["US08_BirthBeforeMarriageOfParents"] += 1
                    except KeyError:
                        pass

                if self.individualdata[husband_individiual_id]["DIVDATE"] != "NA":
                    c_Parents_DivDate = datetime.datetime.strptime(
                        self.individualdata[husband_individiual_id]["DIVDATE"], '%d %b %Y')
                    try:
                        if (c_birthday - c_Parents_DivDate).days > 270:
                            print(
                                "ERROR: US08 Family {} has Child {} with Birth date '{}' who was born 9 Months after Divorce of parents '{}'"
                                    .format(key, child_firstname, self.individualdata[child]["BIRTDATE"],
                                            self.individualdata[husband_individiual_id]["DIVDATE"]))
                            self.errorLog["US08_BirthBeforeMarriageOfParents"] += 1
                    except KeyError:
                        pass

                if self.individualdata[husband_individiual_id]["DEATDATE"] != "NA":
                    c_Father_DeathDate = datetime.datetime.strptime(
                        self.individualdata[husband_individiual_id]["DEATDATE"], '%d %b %Y')
                    try:
                        if (c_birthday - c_Father_DeathDate).days > 270:
                            print(
                                "ERROR: US09 Family {} has Child {} with Birth date '{}' who was born after 9 months after Fathers Death '{}'"
                                    .format(key, child_firstname, self.individualdata[child]["BIRTDATE"],
                                            self.individualdata[husband_individiual_id]["DEATDATE"]))
                            self.errorLog["US09_BirthBeforeDeathOfParents"] += 1
                    except KeyError:
                        pass

                if self.individualdata[wife_individiual_id]["DEATDATE"] != "NA":
                    c_Mother_DeathDate = datetime.datetime.strptime(
                        self.individualdata[wife_individiual_id]["DEATDATE"], '%d %b %Y')
                    try:
                        if (c_birthday - c_Mother_DeathDate).days > 0:
                            print(
                                "ERROR: US09 Family {} has Child {} with Birth date '{}' who was born after mothers death '{}'"
                                    .format(key, child_firstname, self.individualdata[child]["BIRTDATE"],
                                            self.individualdata[wife_individiual_id]["DEATDATE"]))
                            self.errorLog["US09_BirthBeforeDeathOfParents"] += 1
                    except KeyError:
                        pass

                if self.individualdata[child]["SEX"] == "M":
                    child_firstname, child_lastname = self.individualdata[child]["NAME"].split()
                    if child_lastname != husband_lastname:
                        print(
                            "ERROR: US16 INDIVIDUAL {} {} and INDIVIDUAL {} {} have a Father-Child relationship but have different last names".format(
                                husband_individiual_id, husband_firstname + husband_lastname, child,
                                self.individualdata[child]["NAME"]))
                        self.errorLog["US16_MaleLastNames"] += 1

            try:
                marriage = self.individualdata[husband_individiual_id]["MARRDATE"]
            except KeyError:
                return "No Marriage date found"

            try:
                divorce = self.individualdata[husband_individiual_id]["DIVDATE"]
            except KeyError:
                divorce = "NA"

            try:
                child = value["CHIL"]
                self.check_US13_US14(child, key)
            except KeyError:
                child = "NA"
            except ValueError as e:
                print(e)

            if self.individualdata[husband_individiual_id]["AGE"] > 2 * (
                    self.individualdata[wife_individiual_id]["AGE"]):
                print("ERROR: US34 INDIVIDUAL {} {} and INDIVIDUAL {} {} have large age difference".format(
                    husband_individiual_id, husband_name, wife_individiual_id,
                    self.individualdata[wife_individiual_id]["NAME"]))
                self.errorLog["US34_AgeDifference"] += 1

            if self.individualdata[wife_individiual_id]["AGE"] > 2 * (
                    self.individualdata[husband_individiual_id]["AGE"]):
                print("ERROR: US34 INDIVIDUAL {} {} and INDIVIDUAL {} {} have large age difference".format(
                    wife_individiual_id, wife_name, husband_individiual_id,
                    self.individualdata[husband_individiual_id]["NAME"]))
                self.errorLog["US34_AgeDifference"] += 1

            if "FAMC" in self.individualdata[husband_individiual_id] and "FAMC" in self.individualdata[
                wife_individiual_id]:
                if self.individualdata[husband_individiual_id]["FAMC"] == self.individualdata[wife_individiual_id][
                    "FAMC"]:
                    print(
                        "ERROR: US18 INDIVIDUAL {} {} and INDIVIDUAL {} {} are siblings but have married".format(
                            husband_individiual_id, husband_firstname, wife_individiual_id, wife_firstname))
                    self.errorLog["US18_SiblingMarriageError"] += 1

            if (divorce != "NA") and (div_husband != "NA") and (div_wife != "NA"):
                if (datetime.datetime.strptime(marriage, '%d %b %Y') > datetime.datetime.strptime(
                        self.individualdata[husband_individiual_id]["DIVDATE"], '%d %b %Y')) \
                        or (datetime.datetime.strptime(self.individualdata[wife_individiual_id]["MARRDATE"],
                                                       '%d %b %Y') > datetime.datetime.strptime(
                    self.individualdata[wife_individiual_id]["DIVDATE"], '%d %b %Y')):
                    print("ERROR: US04 INDIVIDUAL {} {} has Marriage After Divorce".format(husband_individiual_id,
                                                                                           husband_name))
                    self.errorLog["US04_MarriageOccursBeforeDivorce"] += 1

            if (self.individualdata[husband_individiual_id]["SEX"] == "M" and self.individualdata[wife_individiual_id][
                "SEX"] == "M"):
                print("ERROR: US21 INDIVIDUAL {} {} and INDIVIDUAL {} {} are of same gender but have married".format(
                    husband_individiual_id, husband_name, wife_individiual_id, wife_name))
                self.errorLog["ProperGender"] += 1

            self.prettytablefamily.add_row(
                [key, marriage, divorce, husband_individiual_id, husband_name, wife_individiual_id, wife_name, child])

            # Next 10 lines of code is for testing if the individual and family records is consistent with each other
            US26_IDs[husband_individiual_id] += 1
            US26_IDs[wife_individiual_id] += 1
            for i in child:
                US26_IDs[i] += 1

        for indiv_id in self.individualdata.keys():
            if indiv_id not in US26_IDs.keys():
                self.errorLog['US26_Corresponding_entries'] += 1
                print("Error: US26 INDIVIDUAL {} the information in the individual and family records is not consistent"
                      .format(indiv_id))

    def checkMarriageBeforeDeath(self, death_date, marriage, key):
        """ if the death is before marriage, raise KeyError """
        death_date = datetime.datetime.strptime(death_date, '%d %b %Y')
        marr_date = datetime.datetime.strptime(marriage, '%d %b %Y')
        result = death_date - marr_date

        if result.days < 0:
            print("ERROR: US05: marriage can't be after death for {}".format(self.individualdata[key]["NAME"]))
            self.errorLog["US05_checkMarriageBeforeDeath"] += 1

    def check_divorce(self, divorce, death, key):
        """ if the divorce is after death, raise KeyError """
        div_date = datetime.datetime.strptime(divorce, '%d %b %Y')
        death_date = datetime.datetime.strptime(death, '%d %b %Y')
        result = death_date - div_date

        if result.days < 0:
            print("ERROR: US06: divorce can't be after death date for  {}".format(self.individualdata[key]["NAME"]))
            self.errorLog["US06_check_divorce"] += 1

    def check_US13_US14(self, sibling_list, key):
        """ this function check for:
            - US13 ( Birth dates of siblings should be more than 8 months apart or less than2 days apart, like twins )
            - US14 ( No more than five siblings should be born at the same time )
        """
        children = dict()
        for indiv_id in sibling_list:
            children[indiv_id] = datetime.datetime.strptime(self.individualdata[indiv_id]["BIRTDATE"], '%d %b %Y')

        twins = defaultdict(int)
        US13_siblings = defaultdict(int)

        # to compare between two siblings
        for ID_1, first in children.items():
            for ID_2, second in children.items():

                if ID_1 == ID_2:
                    continue

                difference = first - second
                if 1 >= difference.days >= -1:
                    twins[ID_2] += 1

                elif 240 >= difference.days >= -240:
                    self.errorLog["US13 Siblings spacing:"] += 0.5
                    US13_siblings[ID_2] += 1

        if len(US13_siblings.keys()) > 0:
            print("ERROR: US13 Siblings spacing: "
                  "Birth dates of siblings with ID {}, should be more than 8 months apart or less than2 days apart, "
                  "like twins".format(list(US13_siblings.keys())))

        if len(twins) > 5:
            self.errorLog["US14 Multiple births <= 5:"] += 1
            raise ValueError("ERROR: US14 Multiple births <= 5: "
                             "No more than five siblings should be born at the same time in family with ID: {}."
                             .format(key))

    def donothing(self, nothing):
        pass


def main():
    file_name = input("Enter file name: \n")
    pretty = input("Do you want pretty table? y/n \n")
    g = Gedcom(file_name, pretty)
    print(g.analyze_gedcom_file())
    print(g.prettytableindividuals)
    print(g.prettytablefamily)


if __name__ == '__main__':
    main()
