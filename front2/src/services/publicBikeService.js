import api from "../api/axios";
import {
  BIKE_HERO_STATS,
  STATIONS_MOCK,
  HOURLY_USAGE,
  MONTHLY_USAGE,
  TOP_STATIONS,
  AGE_DISTRIBUTION,
  AI_INSIGHTS,
  ROUTES_MOCK,
  FORECAST_STATIONS,
} from "../constants/mockData";

// GET /bike/seoul/summary
async function getSummary() {
  try {
    const response = await api.get("/bike/seoul/summary");
    const resData = response.data;
    const summaryData = resData?.data ?? resData;

    const totalBikes = summaryData?.total_bikes ?? 100;
    const activeStations = summaryData?.active_stations ?? 20;

    const result = [
      {
        label: "오늘 총 대여",
        value: `${totalBikes.toLocaleString()}대`,
        change: "+8.4%",
      },
      {
        label: "운영 대여소",
        value: `${activeStations.toLocaleString()}개소`,
        change: "+2.1%",
      },
      {
        label: "현재 이용 중",
        value: "4,318대",
        change: "+12.3%",
      },
      {
        label: "평균 이용 시간",
        value: "17.4분",
        change: "-1.8%",
      },
    ];
    return result;
  } catch (err) {
    console.error("[Summary API 에러]:", err);
    return [
      { label: "오늘 총 대여", value: "100대", change: "0%" },
      { label: "운영 대여소", value: "20개소", change: "0%" },
      { label: "현재 이용 중", value: "0대", change: "0%" },
      { label: "평균 이용 시간", value: "0분", change: "0%" },
    ];
  }
}

// GET /bike/seoul/routes
async function getBikeRoutes() {
  try {
    const { data } = await api.get("/bike/seoul/routes");
    if (!Array.isArray(data) || data.length === 0) {
      return ROUTES_MOCK.filter((r) => r.bikeType === "따릉이");
    }
    return data;
  } catch (err) {
    console.error("[Routes API 에러]:", err);
    return ROUTES_MOCK.filter((r) => r.bikeType === "따릉이");
  }
}

// GET /bike/stations
async function getStations() {
  try {
    const { data } = await api.get("/bike/stations");
    return {
      stations: data?.stations ?? STATIONS_MOCK,
      hourlyUsage: data?.hourlyUsage ?? HOURLY_USAGE
    };
  } catch (err) {
    console.error("[Stations API 에러]:", err);
    return { stations: STATIONS_MOCK, hourlyUsage: HOURLY_USAGE };
  }
}

// GET /ai/bike/analysis 
async function getAnalysis() {
  try {
    const response = await api.get("/ai/bike/analysis");

    const data = response.data;
    const analysisData = data?.data ?? data; 
    
    const result = {
      monthlyUsage: analysisData?.monthlyUsage ?? MONTHLY_USAGE,
      topStations: analysisData?.topStations ?? TOP_STATIONS,
      ageDistribution: analysisData?.ageDistribution ?? AGE_DISTRIBUTION,
      insights: analysisData?.insights ?? AI_INSIGHTS,
    };
    return result;
  } catch (err) { 
    console.error("[Analysis API 에러]:", err);
    return {
      monthlyUsage: MONTHLY_USAGE,
      topStations: TOP_STATIONS,
      ageDistribution: AGE_DISTRIBUTION,
      insights: AI_INSIGHTS,
    };
  }
}

// POST /ai/bike/forecast 
async function getForecast({
  stationId,
  date,
  hour,
  isHoliday,
  temperature,
  humidity,
  rainfall,
  windSpeed,
  recentHourlyRentals,
  prevDaySameHourRentals,
  rolling7dSameHourAvg,
}) {
  try {
    const { data } = await api.post("/ai/bike/forecast", { 
      station_id: stationId,
      date,
      hour,
      is_holiday: isHoliday ? 1 : 0,
      temperature,
      humidity,
      rainfall,
      wind_speed: windSpeed,
      recent_1h_rental_count: recentHourlyRentals,
      prev_day_same_hour_rental_count: prevDaySameHourRentals,
      rolling_7d_same_hour_avg: rolling7dSameHourAvg,
    });
    return data;
  } catch (err) {
    console.error("[Forecast API 에러]:", err);
    return mockForecast({
      stationId,
      isHoliday,
      temperature,
      rainfall,
      windSpeed,
      recentHourlyRentals,
      prevDaySameHourRentals,
      rolling7dSameHourAvg,
    });
  }
}

function mockForecast({
  stationId,
  isHoliday,
  temperature,
  rainfall,
  windSpeed,
  recentHourlyRentals,
  prevDaySameHourRentals,
  rolling7dSameHourAvg,
}) {
  const station = FORECAST_STATIONS.find((s) => s.id === stationId) ?? FORECAST_STATIONS[0];

  let weatherFactor = 1;
  if (rainfall > 0) weatherFactor *= 0.6;
  if (temperature < 5 || temperature > 33) weatherFactor *= 0.8;
  if (windSpeed > 8) weatherFactor *= 0.9;
  if (isHoliday) weatherFactor *= 1.15;

  const baseDemand = recentHourlyRentals * 0.4 + prevDaySameHourRentals * 0.3 + rolling7dSameHourAvg * 0.3;
  const predicted_demand = Math.max(0, Math.round(baseDemand * weatherFactor));
  const capacityRatio = station.rackCount > 0 ? predicted_demand / station.rackCount : 0;

  const demand_level = capacityRatio >= 0.8 ? "높음" : capacityRatio >= 0.5 ? "보통" : "낮음";
  const shortage_risk = capacityRatio >= 0.8;
  const message =
    demand_level === "높음"
      ? "해당 시간대 수요가 매우 높습니다. 인근 대여소 재배치를 권장합니다."
      : demand_level === "보통"
        ? "해당 시간대 수요가 보통 수준입니다. 현재 대여소 운영을 유지해도 좋습니다."
        : "해당 시간대 수요가 낮습니다. 자전거 재배치가 필요하지 않습니다.";

  return { predicted_demand, demand_level, shortage_risk, message };
}

const publicBikeService = { 
  getSummary, 
  getBikeRoutes, 
  getRoutes: getBikeRoutes,
  getStations, 
  getAnalysis, 
  getForecast 
};

export default publicBikeService;