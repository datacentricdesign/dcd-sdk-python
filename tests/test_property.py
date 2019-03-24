from dcd.entities.property import Property

import unittest

class PropertyTest(unittest.TestCase):

    def test_align(self):
        test_val1 = ([5,1],[10,2],[15,3])
        test_val2 = ([0,1],[2,1],[6,1],[8,1],[10,2],[13,3],[13,3])
        p1 = Property("test", values=test_val1)
        p2 = Property("test2", values=test_val2)
        p1.align_values_to(p2)
        print(p1)


if __name__ == '__main__':
    unittest.main()