import pytest
from src.domain.models import Part, Supplier, ProductionLine, SimulationContext

class MockPriceHikeStrategy:
    pass

def test_price_hike_strategy_calculation():
    from src.domain.strategies import PriceHikeStrategy
    
    # Arrange
    part = Part(id="P1", name="Part1", supplier_id="S1", unit_price=100.0, current_inventory=10, daily_usage_rate=1)
    context = SimulationContext(
        parts=[part],
        suppliers=[],
        production_lines=[]
    )
    
    # Act
    strategy = PriceHikeStrategy(price_increase_pct=20.0)
    result = strategy.calculate(context)
    
    # Assert
    assert result.profit_delta == -600.0

def test_delay_impact_strategy_calculation():
    from src.domain.strategies import DelayImpactStrategy
    
    # Arrange
    # 시나리오: 일일 생산량 100, 지연 10일
    # 안전 재고 기간 5일로 가정하면, 실제 지연 피해는 5일분.
    line = ProductionLine(id="L1", name="Line1", capacity_per_day=100, efficiency_rate=1.0)
    context = SimulationContext(
        parts=[],
        suppliers=[],
        production_lines=[line]
    )
    
    # Act
    # 10일 지연
    strategy = DelayImpactStrategy(delay_days=10)
    result = strategy.calculate(context)
    
    # Assert
    # 손실 = (10 - 5) * 100 = 500
    assert result.production_loss == 500
