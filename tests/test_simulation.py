import pytest
from src.data_loader import generate_synthetic_data
from src.simulation import calculate_impact

@pytest.fixture
def mock_data():
    return generate_synthetic_data()

def test_simulation_no_change(mock_data):
    """Verify that 0% price change and 0 delay results in zero delta."""
    results = calculate_impact(mock_data, price_increase_pct=0, delay_days=0)
    
    assert results['before']['operating_profit'] == results['after']['operating_profit']
    assert results['delta']['profit_change'] == 0
    assert results['delta']['production_loss'] == 0

def test_simulation_price_increase(mock_data):
    """Verify that price increase reduces profit."""
    results = calculate_impact(mock_data, price_increase_pct=20, delay_days=0)
    
    # Cost should go up
    assert results['after']['material_cost'] > results['before']['material_cost']
    # Profit should go down
    assert results['after']['operating_profit'] < results['before']['operating_profit']
    
def test_simulation_delay_impact(mock_data):
    """Verify that large delays reduce production output."""
    # Delay of 10 days (safety stock is 5, so 5 days lost)
    results = calculate_impact(mock_data, price_increase_pct=0, delay_days=10)
    
    assert results['delta']['production_loss'] > 0
    assert results['after']['production_units'] < results['before']['production_units']
