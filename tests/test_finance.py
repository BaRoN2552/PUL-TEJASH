import unittest
import asyncio
from bot.database import init_db
from bot.services.finance_service import finance_service

class TestFinanceService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize db before running tests
        asyncio.run(init_db())

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_user_and_default_account_creation(self):
        async def test():
            # Clean/random ID to avoid conflicts
            user_id = 99912345
            user = await finance_service.get_or_create_user(user_id, "testuser", "Test User")
            
            self.assertEqual(user.id, user_id)
            self.assertEqual(user.username, "testuser")
            self.assertEqual(user.full_name, "Test User")
            
            # Check default "Naqd" account auto-created
            accounts = await finance_service.get_user_accounts(user_id)
            self.assertEqual(len(accounts), 1)
            self.assertEqual(accounts[0].name, "Naqd")
            self.assertEqual(accounts[0].currency, "UZS")
            self.assertEqual(float(accounts[0].balance), 0.0)
        self.loop.run_until_complete(test())

if __name__ == "__main__":
    unittest.main()
