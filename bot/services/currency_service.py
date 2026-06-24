import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class CurrencyService:
    def __init__(self):
        self._rates: Dict[str, float] = {"UZS": 1.0}
        self._last_fetch: Optional[datetime] = None
        self._cache_ttl = timedelta(hours=6)
        self._api_url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"

    async def fetch_rates(self) -> bool:
        """Fetch currency rates from Central Bank of Uzbekistan API."""
        now = datetime.now()
        if self._last_fetch and (now - self._last_fetch) < self._cache_ttl:
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self._api_url)
                if response.status_code == 200:
                    data = response.json()
                    # Reset rates but keep UZS as base
                    self._rates = {"UZS": 1.0}
                    for item in data:
                        ccy = item.get("Ccy")
                        rate_str = item.get("Rate")
                        if ccy and rate_str:
                            try:
                                self._rates[ccy.upper()] = float(rate_str)
                            except ValueError:
                                continue
                    self._last_fetch = now
                    logger.info("Successfully fetched currency rates from CBU.")
                    return True
                else:
                    logger.error(f"Failed to fetch rates from CBU. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching currency rates from CBU: {e}")
        
        # If fetch fails but we have cached rates, proceed
        return len(self._rates) > 1

    async def get_rate(self, currency: str) -> float:
        """Get the rate of a currency to UZS (e.g. how many UZS is 1 USD)."""
        currency = currency.upper()
        if currency == "UZS":
            return 1.0
        
        # Ensure we have loaded rates
        await self.fetch_rates()
        
        # If currency is not found, fallback to 1.0 or check common defaults
        if currency not in self._rates:
            logger.warning(f"Currency '{currency}' not found in fetched rates. Using default/fallback.")
            # Hardcoded fallbacks if API is down and cache is empty
            fallbacks = {"USD": 12800.0, "EUR": 13800.0, "RUB": 140.0}
            return fallbacks.get(currency, 1.0)
            
        return self._rates[currency]

    async def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount from one currency to another."""
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency == to_currency:
            return amount

        rate_from = await self.get_rate(from_currency)
        rate_to = await self.get_rate(to_currency)

        # Convert to UZS first
        amount_uzs = amount * rate_from
        
        # Convert from UZS to target
        converted_amount = amount_uzs / rate_to
        return round(converted_amount, 2)

currency_service = CurrencyService()
