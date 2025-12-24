from typing import List, Optional
from domain.models import SimulationContext, SimulationResult, Part, Supplier, ProductionLine
from domain.interfaces import ISimulationStrategy
from domain.strategies import PriceHikeStrategy, DelayImpactStrategy

class SimulationService:
    """
    SimulationService (Facade Pattern)
    - UI 레이어는 구체적인 전략 클래스를 알 필요 없이 이 서비스를 통해 시뮬레이션을 요청한다.
    - 여러 전략을 복합적으로 적용하는 로직을 담당한다.
    """
    def __init__(self, context: SimulationContext):
        self.context = context
    
    def run_simulation(self, price_increase_pct: float, delay_days: int) -> SimulationResult:
        """
        사용자 입력(가격, 지연)을 받아 적절한 전략을 수립하고 실행 결과를 합산 반환한다.
        """
        strategies: List[ISimulationStrategy] = []
        
        # 전략 선택 로직 (Factory 역할 겸임)
        if price_increase_pct != 0:
            strategies.append(PriceHikeStrategy(price_increase_pct))
            
        if delay_days > 0:
            strategies.append(DelayImpactStrategy(delay_days))
            
        # 결과 합산 (Composite Pattern과 유사한 접근)
        final_result = SimulationResult(
            operating_profit=0, # 추후 Base Calculation 로직 필요, 지금은 Delta 중심
            production_output=0,
            profit_delta=0.0,
            production_loss=0
        )
        
        # Base Data Calculation (Baseline)
        # 실제 구현에서는 Repository에서 기본 Profit/Production을 가져와야 함.
        # 여기서는 Delta 누적만 수행.
        
        for strategy in strategies:
            result = strategy.calculate(self.context)
            final_result.profit_delta += result.profit_delta
            final_result.production_loss += result.production_loss
            
        return final_result
