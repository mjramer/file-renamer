import src.rename.file_renamer as renamer
import os
import unittest

DATA_PATH = "data/"
SOLUTIONS = {
                "Duplicate.txt" : "renamed-single-pdfs/Teen Site 41 11.16.23.pdf",
                "Signature Interference.txt" : "renamed-single-pdfs/Teen Site 143 11.28.23.pdf",
                "Site Template.txt" : "renamed-single-pdfs/Site 212 11.27.23.pdf",
                "SNL No Site.txt" : "renamed-single-pdfs/no-site-id-found-",
                "SNL Template.txt" : "renamed-single-pdfs/Site 13 9.29.23.pdf",
                "Teen Template.txt" : "renamed-single-pdfs/Teen Site 41 11.16.23.pdf"
             }

class FileRenamerMethods(unittest.TestCase):

    def test_extract_date_double_dig_month_good_format(self):
        expected = "12/23/23"
        actual = renamer.extract_date_double_dig_month(expected)
        self.assertEqual(actual, expected)

    def test_extract_date_double_dig_month_bad_format(self):
        expected = "12/23/23"
        actual = renamer.extract_date_double_dig_month("bcdiwb" + expected + "fdnjofnw")
        self.assertEqual(actual, expected)
    
    def test_extract_date_double_dig_month_fail(self):
        expected = "12/23/23"
        actual = renamer.extract_date_double_dig_month("bcdiwb" + expected[0:-1] + "fdnjofnw")
        self.assertNotEqual(actual, expected)
    
    def test_extract_date_single_dig_month_good_format(self):
        expected = "2/23/23"
        actual = renamer.extract_date_single_dig_month(expected)
        self.assertEqual(actual, expected)

    def test_extract_date_single_dig_month_bad_format(self):
        expected = "2/23/23"
        actual = renamer.extract_date_single_dig_month("bcdiwb" + expected + "fdnjofnw")
        self.assertEqual(actual, expected)
    
    def test_extract_date_single_dig_month_fail(self):
        expected = "2/23/23"
        actual = renamer.extract_date_single_dig_month("bcdiwb" + expected[0:-1] + "fdnjofnw")
        self.assertNotEqual(actual, expected)

    def test_generate_file_name(self):
        for text_file in os.listdir(DATA_PATH):
            with open(DATA_PATH + text_file) as f:
                data = f.read()
                actual = renamer.generate_file_name(data)
                expected = SOLUTIONS[text_file]
                try:
                    self.assertTrue(expected in actual)
                except AssertionError as msg:
                    print("Actual: " + actual + " | Expected: " + expected)

if __name__ == '__main__':
    unittest.main()
    # with open ("data/SNL No Site.txt") as f:
    #     data = f.read()
    #     print(renamer.generate_file_name(data))