import os
import shutil
import unittest

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


from ggit import *

def func(x, a, b, c):
    return a * np.exp(-b * x) + c

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
        x, y = [], []
        for num in range(200):
            start_time = time.time()
            filename = f"file{num}.txt"
            dirname = f"dir{num}"
            with open(filename, 'w') as fh:
                fh.write(f"test contents{num}")
            os.mkdir(dirname)
            with open(f"{dirname}/{filename}", 'w') as fh:
                fh.write(f"test DIR contents{num}")
            Ggit.add(["."])
            Ggit.commit()
            end_time = time.time() - start_time
            print(f"Git test({num}): %.2fs."%end_time)
            x.append(num)
            y.append(end_time)
            print('\n')
        popt, pcov = curve_fit(func, x, y, maxfev=1000000)
        plt.plot(x,y)
        plt.plot(x, [func(xi, *popt) for xi in x], 'r-')
        plt.show()
        print(51, popt)

if __name__ == '__main__':
    unittest.main()

