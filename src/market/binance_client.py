from typing import Any

import httpx

from src.models.candle import Candle


class BinanceMarketClient:
    def __init__(
        self,
        base_url: str = "https://data-api.binance.vision",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 5,
    ) -> list[Candle]:
        endpoint = "/api/v3/klines"

        parameters = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit,
        }

        with httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = client.get(
                endpoint,
                params=parameters,
            )
            response.raise_for_status()

        data: Any = response.json()

        if not isinstance(data, list):
            raise ValueError(
                "Resposta inesperada da API de mercado"
            )

        candles: list[Candle] = []

        for item in data:
            candle = Candle(
                open_time=int(item[0]),
                open_price=float(item[1]),
                high_price=float(item[2]),
                low_price=float(item[3]),
                close_price=float(item[4]),
                volume=float(item[5]),
            )

            candles.append(candle)

        return candles