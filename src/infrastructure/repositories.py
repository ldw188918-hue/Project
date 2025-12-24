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
    - 현재는 내부 mock 데이터를 사용하거나 CSV 파일 업로드를 지원합니다.
    """
    
    def load_context(self) -> SimulationContext:
        """기본 mock 데이터로 컨텍스트 로드"""
        raw_data = _generate_mock_data()
        return self._build_context(raw_data)
    
    def load_context_from_uploads(
        self, 
        parts_csv=None, 
        suppliers_csv=None, 
        production_csv=None
    ) -> SimulationContext:
        """업로드된 CSV 파일로부터 컨텍스트 로드
        
        Args:
            parts_csv: 부품 데이터 CSV 파일 (UploadedFile 객체)
            suppliers_csv: 공급사 데이터 CSV 파일
            production_csv: 생산라인 데이터 CSV 파일
            
        Returns:
            SimulationContext: 업로드된 데이터 또는 mock 데이터로 생성된 컨텍스트
        """
        # 기본 mock 데이터 먼저 로드
        raw_data = _generate_mock_data()
        
        # 업로드된 파일이 있으면 덮어쓰기
        # 업로드된 파일이 있으면 덮어쓰기
        try:
            if parts_csv is not None:
                print(f"DEBUG: parts_csv type: {type(parts_csv)}")
                if hasattr(parts_csv, 'seek'):
                    parts_csv.seek(0)
                raw_data['parts'] = pd.read_csv(parts_csv)
            if suppliers_csv is not None:
                print(f"DEBUG: suppliers_csv type: {type(suppliers_csv)}")
                if hasattr(suppliers_csv, 'seek'):
                    suppliers_csv.seek(0)
                raw_data['suppliers'] = pd.read_csv(suppliers_csv)
            if production_csv is not None:
                print(f"DEBUG: production_csv type: {type(production_csv)}")
                if hasattr(production_csv, 'seek'):
                    production_csv.seek(0)
                raw_data['production'] = pd.read_csv(production_csv)
        except Exception as e:
            print(f"ERROR in load_context_from_uploads: {e}")
            # 에러 발생 시 로그를 남기거나 처리할 수 있음 (여기선 간단히 pass 또는 re-raise)
            # print(f"Error reading CSV: {e}")
            raise e
        
        return self._build_context(raw_data)
    
    
    def _standardize_columns(self, df: pd.DataFrame, target_type: str) -> pd.DataFrame:
        """
        데이터프레임의 컬럼명을 표준 스키마로 매핑한다.
        (한글, 영어, 다양한 별칭 지원)
        """
        # 매핑 정의 (표준 컬럼명 -> [가능한 별칭들])
        # 대소문자는 무시하고 비교함
        mappings = {}
        
        if target_type == 'parts':
            mappings = {
                'Part_ID': ['id', 'part_id', 'item_id', 'code', '품목코드', '부품코드', '코드', '제품코드'],
                'Part_Name': ['name', 'part_name', 'item_name', '품목명', '부품명', '이름', '품명'],
                'Supplier_ID': ['supplier_id', 'vendor_id', 'partner_id', '공급사코드', '업체코드', '공급사'],
                'Unit_Price': ['price', 'unit_price', 'cost', 'unit_cost', 'amount', '단가', '가격', '비용', '금액'],
                'Current_Inventory': ['inventory', 'stock', 'qty', 'quantity', 'current_stock', '재고', '현재재고', '수량', '보유량'],
                'Daily_Usage_Rate': ['usage', 'daily_usage', 'rate', 'demand', 'consumption', '일일사용량', '사용량', '소요량', '일일소요량']
            }
        elif target_type == 'suppliers':
            mappings = {
                'Supplier_ID': ['id', 'supplier_id', 'vendor_id', 'code', '공급사코드', '업체코드'],
                'Supplier_Name': ['name', 'supplier_name', 'vendor_name', 'company', '공급사명', '업체명', '회사명'],
                'Risk_Score': ['risk', 'risk_score', 'score', 'credit', '리스크', '위험도', '신용도', '점수'],
                'Base_Lead_Time_Days': ['lead_time', 'leadtime', 'days', 'lt', 'time', '리드타임', '납기', '소요일']
            }
        elif target_type == 'production':
            mappings = {
                'Line_ID': ['id', 'line_id', 'line', 'code', '라인코드', '생산라인'],
                'Line_Name': ['name', 'line_name', '라인명', '이름'],
                'Capacity_Per_Day': ['capacity', 'capa', 'output', 'daily_capa', '생산능력', '일일생산량', 'capa'],
                'Efficiency_Rate': ['efficiency', 'eff', 'rate', 'yield', '효율', '수율', '가동률']
            }
            
        # 컬럼 변경
        new_columns = {}
        for col in df.columns:
            col_lower = str(col).lower().replace(" ", "_").strip() # 소문자 및 공백 처리
            
            # 매핑 찾기
            found = False
            for std_col, aliases in mappings.items():
                if col_lower == std_col.lower(): # 이미 표준 이름인 경우
                    found = True
                    break
                if col_lower in aliases:
                    new_columns[col] = std_col
                    found = True
                    break
            
        if new_columns:
            print(f"DEBUG: Renaming columns for {target_type}: {new_columns}")
            return df.rename(columns=new_columns)
            
        return df

    def _build_context(self, raw_data: dict) -> SimulationContext:
        """DataFrame을 도메인 모델로 변환"""
        
        try:
            # 1. Suppliers
            suppliers = []
            if 'suppliers' in raw_data and not raw_data['suppliers'].empty:
                # 컬럼 표준화 적용
                df = self._standardize_columns(raw_data['suppliers'], 'suppliers')
                
                # 필수 컬럼 검사
                required_cols = ['Supplier_ID', 'Supplier_Name', 'Risk_Score', 'Base_Lead_Time_Days']
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    raise ValueError(f"공급사 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing)}")

                for _, row in df.iterrows():
                    suppliers.append(Supplier(
                        id=row['Supplier_ID'],
                        name=row['Supplier_Name'],
                        risk_score=row['Risk_Score'],
                        base_lead_time_days=int(row['Base_Lead_Time_Days'])
                    ))
                
            # 2. Parts
            parts = []
            if 'parts' in raw_data and not raw_data['parts'].empty:
                # 컬럼 표준화 적용
                df = self._standardize_columns(raw_data['parts'], 'parts')
                
                required_cols = ['Part_ID', 'Part_Name', 'Supplier_ID', 'Unit_Price', 'Current_Inventory', 'Daily_Usage_Rate']
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    raise ValueError(f"부품 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing)}")

                for _, row in df.iterrows():
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
            if 'production' in raw_data and not raw_data['production'].empty:
                # 컬럼 표준화 적용
                df = self._standardize_columns(raw_data['production'], 'production')
                
                required_cols = ['Line_ID', 'Line_Name', 'Capacity_Per_Day', 'Efficiency_Rate']
                missing = [col for col in required_cols if col not in df.columns]
                if missing:
                    raise ValueError(f"생산라인 파일에 다음 필수 컬럼이 없습니다: {', '.join(missing)}")

                for _, row in df.iterrows():
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
            
        except KeyError as e:
            raise ValueError(f"데이터 컬럼 오류: {str(e)} 컬럼을 찾을 수 없습니다. 컬럼명이 '단가', '재고', '리드타임' 등으로 되어있더라도 자동으로 인식됩니다.")
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"데이터 변환 중 알 수 없는 오류 발생: {str(e)}")
