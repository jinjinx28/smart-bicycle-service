# smart-bicycle-service
smart bicycle service

### 데이터 수집 방식 안내 (`seoul_api.py`)
- 본 프로젝트는 외부 OpenAPI 호출 방식 대신, **서울시 공공데이터 CSV/Excel 파일을 로컬에서 파싱 및 캐싱(`_CACHED_STATIONS`)하는 방식**으로 대여소 및 날씨 데이터를 제공합니다.
- 따라서 별도의 외부 API 키 없이도 로컬 환경에서 원활하게 동작합니다.