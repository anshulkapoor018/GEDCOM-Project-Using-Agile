#!/usr/bin/env python
"""
Project 03
"""

__author__ = "Anshul Kapoor, Aryan Anmol, Abdulellah Shahrani, Pranay Singh"

# defining possible value level and supported tags as global constant
VALID_VALUES = {"0": ["INDI", "HEAD", "TRLR", "NOTE", "FAM"],
                "1": ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
                "2": ["DATE"]}

class Gedcom:
    def __init__(self, path):
        """ init class operation """
        self.path = path
        self.test_file = self.path
        self.output = []
        self.gedcom_reading()

    def gedcom_reading(self):
        """ reads gedcom file line by line and populates output list """
        file_name = self.test_file
        try:
            fp = open(file_name, 'r', encoding='utf-8')
        except FileNotFoundError as file_not_found:
            raise file_not_found
        else:
            with fp:
                for line in fp:
                    self.output.append("--> " + line.strip('\n'))
                    current_line = line.strip().split(' ')
                    if len(current_line) > 2:
                        if current_line[0] not in ["0", "1", "2"]:
                            current_line.insert(2, 'N')
                        elif current_line[0] == '0' and current_line[1] == 'INDI' or current_line[1] == 'FAM':
                            current_line.insert(2, 'N')
                        elif current_line[0] == '0' and current_line[2] == 'INDI' or current_line[2] == 'FAM':
                            element = current_line.pop(1)
                            current_line.insert(2, element)
                            current_line.insert(2, 'Y')
                        elif current_line[1] in VALID_VALUES[current_line[0]]:
                            current_line.insert(2, 'Y')
                        else:
                            current_line.insert(2, 'N')

                    elif len(current_line) == 2:
                        if current_line[0] not in ["0", "1", "2"]:
                            current_line.insert(2, 'N')
                        else:
                            if current_line[0] == '0' and current_line[1] == 'INDI' or current_line[1] == 'FAM':
                                current_line.insert(2, 'N')
                            elif current_line[1] in VALID_VALUES[current_line[0]]:
                                current_line.insert(2, 'Y')
                            else:
                                current_line.insert(2, 'N')

                    result = '|'.join(current_line[0:3])
                    result1 = ' '.join(current_line[3:])
                    self.output.append("<-- " + result + '|' + result1)

def ask_gedcomfile(prompt='Enter file name: '):
    name = input(prompt)
    if name[-4:] in {'.ged'}:
        return name
    return ask_gedcomfile(prompt='The file name has to end in ".ged", please retry again: ')


def main():
    file_path = ask_gedcomfile()

    try:
        gedcom_data = Gedcom(file_path)
        for value in gedcom_data.output:
            print(value)
    except FileNotFoundError:
        print(f"No File found at path --> {file_path}")


if __name__ == '__main__':
    main()
