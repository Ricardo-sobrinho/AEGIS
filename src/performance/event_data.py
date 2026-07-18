from dataclasses import dataclass

from src.performance.performance import Performance


@dataclass
class PerformanceUpdatedEvent:
    performance: Performance