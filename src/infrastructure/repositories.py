from typing import List
from src.domain.models import Supplier, Part, ProductionLine, SimulationContext
from src.data_loader import generate_synthetic_data # 기존 로직 재활용하지만 Repository 패턴으로 감쌈

class SimulationRepository:
    """
    SimulationRepository
    - 데이터 소스(CSV, DB, API, Mock)로부터 도메인 모델을 로드한다.
    - 현재는 기존의 generate_synthetic_data 함수를 어댑터 패턴으로 연결.
    """
    def load_context(self) -> SimulationContext:
        raw_data = generate_synthetic_data()
        
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
