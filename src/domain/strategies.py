from src.domain.interfaces import ISimulationStrategy
from src.domain.models import SimulationContext, SimulationResult

class PriceHikeStrategy(ISimulationStrategy):
    def __init__(self, price_increase_pct: float):
        self.price_increase_pct = price_increase_pct

    def calculate(self, context: SimulationContext) -> SimulationResult:
        total_profit_delta = 0.0
        MONTHS_DAYS = 30
        
        for part in context.parts:
            base_cost = part.unit_price * part.monthly_usage
            new_price = part.unit_price * (1 + self.price_increase_pct / 100)
            new_cost = new_price * part.monthly_usage
            cost_increase = new_cost - base_cost
            total_profit_delta -= cost_increase

        return SimulationResult(
            operating_profit=0,
            production_output=0,
            profit_delta=total_profit_delta,
            production_loss=0
        )

class DelayImpactStrategy(ISimulationStrategy):
    def __init__(self, delay_days: int):
        self.delay_days = delay_days

    def calculate(self, context: SimulationContext) -> SimulationResult:
        total_production_loss = 0
        SAFETY_BUFFER_DAYS = 5
        
        # 지연이 안전 재고 기간을 초과할 경우 손실 발생
        if self.delay_days > SAFETY_BUFFER_DAYS:
            lost_days = self.delay_days - SAFETY_BUFFER_DAYS
            
            for line in context.production_lines:
                # 라인별 일일 생산량 * 손실 일수
                line_loss = line.capacity_per_day * lost_days
                total_production_loss += line_loss
                
        return SimulationResult(
            operating_profit=0,
            production_output=0,
            profit_delta=0,
            production_loss=total_production_loss
        )
