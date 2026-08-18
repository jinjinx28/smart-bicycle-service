import api from "../api/axios";
import { ROUTES_MOCK } from "../constants/mockData";

// 1. 전체 루트 조회 (백엔드 데이터 + 목데이터 디자인 병합)
async function getRoutes() {
  try {
    const response = await api.get("/routes");
    const rawData = response.data?.data || response.data;
    const list = Array.isArray(rawData) ? rawData : [];
    
    if (list.length === 0) return ROUTES_MOCK;

    // 백엔드 데이터에 UI 표출용 이미지 및 평점 매핑
    return list.map((item, index) => {
      const mock = ROUTES_MOCK[index % ROUTES_MOCK.length];
      return {
        ...mock,          // 기존 UI가 요구하는 이미지, 평점, 설명 유지
        ...item,          // 백엔드에서 가져온 실제 이름, 거리 반영
        id: item.id || mock.id,
        name: item.name || mock.name,
        image: mock.image,
        rating: mock.rating || 4.8,
        reviews: mock.reviews || 120,
      };
    });
  } catch {
    return ROUTES_MOCK;
  }
}

// 2. 단건 상세 조회
async function getRouteDetail(id) {
  try {
    const response = await api.get(`/routes/${id}`);
    const data = response.data?.data || response.data;
    return data;
  } catch {
    return ROUTES_MOCK.find((r) => r.id === Number(id)) || ROUTES_MOCK[0];
  }
}

// 3. 개인 맞춤형 루트 조회
async function getPersonalRoutes() {
  try {
    const response = await api.get("/routes", { params: { type: "personal" } });
    const rawData = response.data?.data || response.data;
    const list = Array.isArray(rawData) ? rawData : [];

    if (list.length === 0) {
      return ROUTES_MOCK.filter((r) => r.bikeType !== "따릉이");
    }

    return list.map((item, index) => {
      const mock = ROUTES_MOCK[index % ROUTES_MOCK.length];
      return {
        ...mock,
        ...item,
        name: item.name || mock.name,
        image: mock.image,
        rating: mock.rating || 4.9,
        bikeType: item.bikeType || "개인용자전거",
      };
    });
  } catch {
    return ROUTES_MOCK.filter((r) => r.bikeType !== "따릉이");
  }
}

const routeService = { getRoutes, getRouteDetail, getPersonalRoutes };
export default routeService;