from dataclasses import dataclass

from src.portfolio.portfolio import Portfolio


@dataclass
class PortfolioUpdatedEvent:
    portfolio: Portfolio