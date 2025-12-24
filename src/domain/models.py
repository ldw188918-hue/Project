from dataclasses import dataclass
from typing import Optional

@dataclass
class Supplier:
    id: str
    name: str
    risk_score: int
    base_lead_time_days: int

@dataclass
class Part:
    id: str
    name: str
    supplier_id: str
    unit_price: float
    current_inventory: int
    daily_usage_rate: int

    @property
    def monthly_usage(self) -> int:
        return self.daily_usage_rate * 30

@dataclass
class ProductionLine:
    id: str
    name: str
    capacity_per_day: int
    efficiency_rate: float

@dataclass
class SimulationContext:
    """시뮬레이션에 필요한 전체 데이터 컨텍스트"""
    parts: list[Part]
    suppliers: list[Supplier]
    production_lines: list[ProductionLine]

@dataclass
class SimulationResult:
    """시뮬레이션 결과 (KPI)"""
    operating_profit: float
    production_output: int
    profit_delta: float = 0.0
    production_loss: int = 0
