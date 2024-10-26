import unittest
from server import ma_fonction


class TestMonModule(unittest.TestCase):

    def test_ma_fonction(self):
        self.assertEqual(ma_fonction(1), 2)


if __name__ == '__main__':
    unittest.main()
