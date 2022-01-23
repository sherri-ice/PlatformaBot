import unittest
from parameterized import parameterized
from geocode.geo_patcher import get_address_from_coordinates


class GeoPatcherTest(unittest.TestCase):
    @parameterized.expand([
        ["Minsk", "27.561831, 53.902284", "Минск, Беларусь"],
        ["Moscow", "37.617644, 55.755819", "Москва, Россия"],
        ["Paris", "2.351556, 48.856663", "IV округ Парижа, Париж, Франция"],
        ["Madrid", "-3.703978, 40.416766", "Мадрид, Испания"]
    ])
    def test_simple_cities(self, test_name, coords, answer):
        address = get_address_from_coordinates(coords)
        self.assertEqual(answer, address)

    @parameterized.expand([
        ["Egypt red sea", "32.188058, 26.472778", "Египет"],
        ["Chechen", "46.394845, 42.955598, ", "Даттахское сельское поселение, Ножай-Юртовский район, Чеченская Республика, Россия"],
    ])
    def test_region_cases(self, test_name, coords, answer):
        address = get_address_from_coordinates(coords)
        self.assertEqual(answer, address)

    @parameterized.expand([
        ["Arabic", "41.006543, 28.978798", "Минск, Беларусь"]
    ])
    def test_cities_cant_be_decoded(self, test_name, coords, answer):
        self.assertRaises(IndexError, get_address_from_coordinates, coords)


if __name__ == '__main__':
    unittest.main()
