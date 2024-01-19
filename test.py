import os
import shutil
import unittest

from ggit import *

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        if os.path.isdir('test'):
            print("removing old test folder...")
            shutil.rmtree("test")
        os.mkdir("test")
        os.chdir("test")
        Ggit.init()

    def tearDown(self):
        # shutil.rmtree("test")
        pass
    
    def test_main(self):
        for num in range(10):
            filename = f"file{num}.txt"
            dirname = f"dir{num}"
            with open(filename, 'w') as fh:
                fh.write(f"test contents{num}")
            os.mkdir(dirname)
            with open(f"{dirname}/{filename}", 'w') as fh:
                fh.write(f"test DIR contents{num}")
            Ggit.add(["."])
            Ggit.commit()

if __name__ == '__main__':
    unittest.main()

