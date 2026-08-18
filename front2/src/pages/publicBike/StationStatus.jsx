import { useEffect, useState } from "react";
import StationCard from "../../components/cards/StationCard";
import AreaChartCard from "../../components/charts/AreaChartCard";
import Loading from "../../components/common/Loading";
import publicBikeService from "../../services/publicBikeService";

const LEGEND = [
  { label: "충분", color: "bg-neon" },
  { label: "부족", color: "bg-warn" },
  { label: "없음", color: "bg-danger" },
];

export default function StationStatus() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchWithCoords = (lat = 37.4979, lng = 127.0276) => {
      publicBikeService.getStations(lat, lng)
        .then((res) => {
          setData(res);
        })
        .catch(() => {
          setData({ stations: [], hourlyUsage: [] });
        });
    };

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
          fetchWithCoords(lat, lng);
        },
        () => {
          // 권한 거부나 타임아웃 발생 시 경고 로그 없이 강남역 좌표로 대체
          fetchWithCoords(37.4979, 127.0276);
        },
        { 
          timeout: 3000, 
          enableHighAccuracy: false 
        }
      );
    } else {
      fetchWithCoords(37.4979, 127.0276);
    }
  }, []);

  if (!data) return <Loading />;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-bike">실시간 현황</p>
          <h2 className="mt-1 text-2xl font-extrabold text-white">내 주변 대여소</h2>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          {LEGEND.map((item) => (
            <span key={item.label} className="flex items-center gap-1.5">
              <span className={`h-2 w-2 rounded-full ${item.color}`} />
              {item.label}
            </span>
          ))}
        </div>
      </div>

      <div className="mb-12 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.stations?.map((station, index) => {
          return (
            <StationCard key={`${station?.id || "station"}-${index}`} station={station} />
          );
        })}
      </div>

      <p className="mb-1 text-sm font-semibold text-bike">시간대 분석</p>
      <h2 className="mb-4 text-2xl font-extrabold text-white">오늘의 시간대별 이용량</h2>
      <AreaChartCard data={data.hourlyUsage} xKey="hour" yKey="count" color="#38BDF8" />
    </div>
  );
}