from bdata.social_network import douban

import unittest

class DoubanTest(unittest.TestCase):
    def test_book_api(self):
        data = douban.get_book_info("30390926")
        print(data)

if __name__ == '__main__':
    unittest.main()