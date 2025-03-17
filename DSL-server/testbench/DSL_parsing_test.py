import unittest
import os
import sys
from pyparsing import ParseException

sys.path.append('/home/carl/DSL-server')
from server.DSL_parser import parser
os.chdir("/home/carl/DSL-server")

class TestParsing(unittest.TestCase):
    def test_parse_script(self):
        for i in range(1,4):
            with open("scripts/results/result" + str(i) + ".txt") as f:
                result = f.readline().strip()
                self.assertEqual(repr(parser.parse_script("scripts/script" + str(i) + ".txt")), result)
        for i in range(1,6):
            with self.assertRaises(ParseException):
                parser.parse_script("scripts/script" + str(i) + " copy.txt")

if __name__ == '__main__':
    unittest.main()