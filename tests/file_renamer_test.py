import src.rename.file_renamer as renamer
import os
import unittest
import multiprocessing

SOLUTIONS = {
                "data/Signature Interference.txt" : "renamed-single-pdfs/Teen Site 143 11.28.23.pdf",
                "data/Site Template.txt" : "renamed-single-pdfs/Site 212 11.27.23.pdf",
                "data/SNL No Site.txt" : "renamed-single-pdfs/no-site-id-found-",
                "data/SNL Template.txt" : "renamed-single-pdfs/Site 13 9.29.23.pdf",
                "data/Teen Template.txt" : "renamed-single-pdfs/Teen Site 41 11.16.23.pdf",
                "data/Teen Template1Duplicate.txt" : "renamed-single-pdfs/Teen Site 41 11.16.23 Duplicate1.pdf"
             }

class FileRenamerMethods(unittest.TestCase):

    # def test_extract_date_double_dig_month_good_format(self):
    #     expected = "12/23/23"
    #     actual = renamer.extract_date_double_dig_month(expected)
    #     self.assertEqual(actual, expected)

    # def test_extract_date_double_dig_month_bad_format(self):
    #     expected = "12/23/23"
    #     actual = renamer.extract_date_double_dig_month("bcdiwb" + expected + "fdnjofnw")
    #     self.assertEqual(actual, expected)
    
    # def test_extract_date_double_dig_month_fail(self):
    #     expected = "12/23/23"
    #     actual = renamer.extract_date_double_dig_month("bcdiwb" + expected[0:-1] + "fdnjofnw")
    #     self.assertNotEqual(actual, expected)
    
    # def test_extract_date_single_dig_month_good_format(self):
    #     expected = "2/23/23"
    #     actual = renamer.extract_date_single_dig_month(expected)
    #     self.assertEqual(actual, expected)

    # def test_extract_date_single_dig_month_bad_format(self):
    #     expected = "2/23/23"
    #     actual = renamer.extract_date_single_dig_month("bcdiwb" + expected + "fdnjofnw")
    #     self.assertEqual(actual, expected)
    
    # def test_extract_date_single_dig_month_fail(self):
    #     expected = "2/23/23"
    #     actual = renamer.extract_date_single_dig_month("bcdiwb" + expected[0:-1] + "fdnjofnw")
    #     self.assertNotEqual(actual, expected)

    # def test_generate_file_name_sync(self):
    #     for text_file in SOLUTIONS.keys():
    #         with open(text_file) as f:
    #             data = f.read()
    #             actual = renamer.generate_file_name(data)
    #             expected = SOLUTIONS[text_file]
    #             self.assertTrue(expected in actual)
    
    def test_generate_file_name_async(self):
        # os.chdir("tests/")
        data_arr = []
        for text_file in SOLUTIONS.keys():
            with open(text_file) as f:
                data = f.read()
                data_arr.append(data)
        
        l = multiprocessing.Lock()
        pool = multiprocessing.Pool(processes=3, initializer=renamer.init, initargs=(l,{}))
        with pool:
            result = pool.map_async(renamer.generate_file_name, data_arr)
            for result in result.get():
                pass

def init(l):
    global lock
    lock = l


if __name__ == "__main__":
    unittest.main()