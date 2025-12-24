# 📁 예시 데이터 파일

이 폴더에는 대시보드에서 테스트할 수 있는 예시 CSV 파일이 들어있습니다.

## 파일 목록

### 1. `parts_example.csv` - 부품 데이터
실제 제조 환경을 반영한 8개의 부품 데이터:
- Steel Sheet (철강 시트)
- Aluminum Frame (알루미늄 프레임)
- Copper Wire (구리 와이어)
- Electronic Board (전자 보드) 등

### 2. `suppliers_example.csv` - 공급사 데이터
3개 국가의 공급사:
- Korea Steel Co. (리스크: 낮음)
- China Manufacturing Ltd. (리스크: 높음)
- Japan Electronics Inc. (리스크: 중간)

### 3. `production_example.csv` - 생산라인 데이터
4개의 생산라인:
- Assembly Line A & B
- Packaging Line
- Quality Control Line

## 사용 방법

1. 대시보드 사이드바에서 "📁 데이터 업로드" 섹션 열기
2. 이 폴더의 CSV 파일들을 업로드
3. 업로드된 데이터로 시뮬레이션 테스트!

## 시나리오 예시

**테스트 시나리오: 중국 공급사 지연 시뮬레이션**
1. `suppliers_example.csv` 업로드 (Risk_Score 0.6)
2. "공급사 납품 지연" 슬라이더를 15일로 설정
3. 생산 차질 및 영업이익 영향 확인
