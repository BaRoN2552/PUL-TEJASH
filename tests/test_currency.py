import unittest
import asyncio
from bot.services.currency_service import currency_service

class TestCurrencyService(unittest.TestCase):
    def setUp(self):
        # Allow async loop to run inside unit tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_convert_same_currency(self):
        async def test():
            val = await currency_service.convert(100.0, "UZS", "UZS")
            self.assertEqual(val, 100.0)
        self.loop.run_until_complete(test())

    def test_get_rate_usd(self):
        async def test():
            rate = await currency_service.get_rate("USD")
            self.assertGreater(rate, 1000.0) # USD rate should be greater than 1000 UZS
        self.loop.run_until_complete(test())

    def test_conversion(self):
        async def test():
            # Test conversion of 10 USD to UZS
            rate_usd = await currency_service.get_rate("USD")
            val = await currency_service.convert(10.0, "USD", "UZS")
            self.assertAlmostEqual(val, 10.0 * rate_usd, places=1)
        self.loop.run_until_complete(test())

if __name__ == "__main__":
    unittest.main()
