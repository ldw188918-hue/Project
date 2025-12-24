from typing import List
import pandas as pd
from domain.models import Supplier, Part, ProductionLine, SimulationContext

def _generate_mock_data():
    """Mock 데이터 생성 (기존 generate_synthetic_data 대체)"""
    
    # Suppliers 데이터
    suppliers_data = {
        'Supplier_ID': ['S1', 'S2', 'S3'],
        'Supplier_Name': ['Supplier A', 'Supplier B', 'Supplier C'],
        'Risk_Score': [0.3, 0.5, 0.2],
        'Base_Lead_Time_Days': [7, 10, 5]
    }
    
    # Parts 데이터
    parts_data = {
        'Part_ID': ['P1', 'P2', 'P3', 'P4', 'P5'],
        'Part_Name': ['Part Alpha', 'Part Beta', 'Part Gamma', 'Part Delta', 'Part Epsilon'],
        'Supplier_ID': ['S1', 'S1', 'S2', 'S2', 'S3'],
        'Unit_Price': [100.0, 150.0, 200.0, 80.0, 120.0],
        'Current_Inventory': [500, 300, 200, 600, 400],
        'Daily_Usage_Rate': [50, 30, 20, 40, 25]
    }
    
    # Production 데이터
    production_data = {
        'Line_ID': ['L1', 'L2', 'L3'],
        'Line_Name': ['Line 1', 'Line 2', 'Line 3'],
        'Capacity_Per_Day': [100, 150, 120],
        'Efficiency_Rate': [0.95, 0.90, 0.92]
    }
    
    return {
        'suppliers': pd.DataFrame(suppliers_data),
        'parts': pd.DataFrame(parts_data),
        'production': pd.DataFrame(production_data)
    }

class SimulationRepository:
    """
    SimulationRepository
    - 데이터 소스(CSV, DB, API, Mock)로부터 도메인 모델을 로드한다.
    - 현재는 내부 mock 데이터를 사용합니다.
    """
    def load_context(self) -> SimulationContext:
        raw_data = _generate_mock_data()
        
        # 1. Suppliers
        suppliers = []
        for _, row in raw_data['suppliers'].iterrows():
            suppliers.append(Supplier(
                id=row['Supplier_ID'],
                name=row['Supplier_Name'],
                risk_score=row['Risk_Score'],
                base_lead_time_days=int(row['Base_Lead_Time_Days'])
            ))
            
        # 2. Parts
        parts = []
        for _, row in raw_data['parts'].iterrows():
            parts.append(Part(
                id=row['Part_ID'],
                name=row['Part_Name'],
                supplier_id=row['Supplier_ID'],
                unit_price=float(row['Unit_Price']),
                current_inventory=int(row['Current_Inventory']),
                daily_usage_rate=int(row['Daily_Usage_Rate'])
            ))
            
        # 3. Production Lines
        lines = []
        for _, row in raw_data['production'].iterrows():
            lines.append(ProductionLine(
                id=row['Line_ID'],
                name=row['Line_Name'],
                capacity_per_day=int(row['Capacity_Per_Day']),
                efficiency_rate=float(row['Efficiency_Rate'])
            ))
            
        return SimulationContext(
            parts=parts,
            suppliers=suppliers,
            production_lines=lines
        )
