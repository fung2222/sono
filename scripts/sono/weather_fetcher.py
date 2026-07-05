#!/usr/bin/env python3
"""
weather_fetcher.py - 拉香港當日 + 5 日天氣預報

Source: Open-Meteo API (https://api.open-meteo.com/v1/forecast)
完全免費、無 API key、支援 HK 座標 (22.28, 114.16)
"""
import urllib.parse
import urllib.request
import json
from datetime import datetime, timedelta


# 香港座標
HK_LAT = 22.28
HK_LON = 114.16
TIMEZONE = 'Asia/Hong_Kong'

# WMO 天氣代碼 → icon + 中文描述
WMO_CODES = {
    0: ('☀️', '天晴'),
    1: ('🌤️', '大致天晴'),
    2: ('⛅', '間中有陽光'),
    3: ('☁️', '多雲'),
    45: ('🌫️', '有霧'),
    48: ('🌫️', '冰霧'),
    51: ('🌦️', '微雨'),
    53: ('🌧️', '毛毛雨'),
    55: ('🌧️', '持續微雨'),
    61: ('🌧️', '微雨'),
    63: ('🌧️', '大雨'),
    65: ('🌧️', '大雨'),
    71: ('🌨️', '微雪'),
    73: ('🌨️', '中雪'),
    75: ('❄️', '大雪'),
    80: ('🌦️', '驟雨'),
    81: ('🌧️', '強驟雨'),
    82: ('⛈️', '暴驟雨'),
    95: ('⛈️', '雷暴'),
    96: ('⛈️', '雷暴夾冰雹'),
    99: ('⛈️', '強雷暴'),
}


def get_wmo_icon(code: int) -> tuple:
    """回傳 (icon, 描述)."""
    return WMO_CODES.get(code, ('🌤️', '多雲'))


def fetch_weather(date: str = None) -> dict:
    """Fetch today's + 5-day forecast for Hong Kong.

    Args:
        date: Optional date string YYYY-MM-DD (default = today HKT)

    Returns: {
        'temp_max': 31,
        'temp_min': 28,
        'icon': '🌧️',
        'desc': '持續微雨，天色多雲',
        'humidity': '69-93%',
        'wind': '西南風 20km/h',
        'uv': '中等',
        'visibility': '良好',
        'forecast': [
            {'weekday': '週三', 'date': '25/6', 'icon': '🌧️', 'temp_max': 32, 'temp_min': 28},
            ...
        ]
    }
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    # Build URL - don't combine start_date/end_date with forecast_days (API rejects)
    params = {
        'latitude': HK_LAT,
        'longitude': HK_LON,
        'daily': 'temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,wind_speed_10m_max',
        'hourly': 'relative_humidity_2m,visibility,uv_index',
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,wind_direction_10m',
        'timezone': TIMEZONE,
        'forecast_days': 5,
    }
    url = 'https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, headers={'User-Agent': 'SonoBot/1.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())

    # Parse result
    current = data.get('current', {})
    daily = data.get('daily', {})
    hourly = data.get('hourly', [])

    # Current weather
    temp_current = round(current.get('temperature_2m', 0))
    weather_code = current.get('weather_code', 0)
    icon, desc = get_wmo_icon(weather_code)

    # Daily extremes
    temp_max_list = daily.get('temperature_2m_max', [])
    temp_min_list = daily.get('temperature_2m_min', [])

    # Build forecast list
    forecast = []
    times = daily.get('time', [])
    dates = daily.get('time', [])
    icons = [get_wmo_icon(c)[0] for c in daily.get('weather_code', [])]
    for i, day_date in enumerate(times):
        dt = datetime.strptime(day_date, '%Y-%m-%d')
        # Weekday in Chinese
        weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
        weekday = weekday_names[dt.weekday()]
        forecast.append({
            'weekday': weekday,
            'date': f"{dt.month}/{dt.day}",
            'icon': icons[i],
            'temp_max': round(temp_max_list[i]),
            'temp_min': round(temp_min_list[i]),
        })

    # Humidity (current hour)
    hour_now = datetime.now().hour
    if hourly:
        humidities = []
        # Get humidity for the same date, every 3 hours
        target_date = date
        for i, hour_time in enumerate(hourly.get('time', [])):
            if hour_time.startswith(target_date):
                humidities.append(hourly.get('relative_humidity_2m', [])[i])
        if humidities:
            min_h = min(humidities)
            max_h = max(humidities)
            humidity_str = f"{min_h}-{max_h}%"
        else:
            humidity_str = '70-85%'
    else:
        humidity_str = '70-85%'

    # Wind (current direction + speed)
    wind_speed = current.get('wind_speed_10m', 0)
    wind_dir_deg = current.get('wind_direction_10m', 0)
    # Direction label
    directions = ['北', '東北', '東', '東南', '南', '西南', '西', '西北']
    if wind_dir_deg:
        idx = int((wind_dir_deg + 22.5) / 45) % 8
        dir_label = directions[idx]
        wind_str = f"{dir_label}風 {wind_speed:.0f}km/h"
    else:
        wind_str = f"{wind_speed:.0f} km/h"

    # UV index (high today)
    uv_indices = []
    if hourly:
        for i, hour_time in enumerate(hourly.get('time', [])):
            if hour_time.startswith(date):
                uvi = hourly.get('uv_index', [])[i]
                if uvi is not None:
                    uv_indices.append(uvi)
        uv_max = max(uv_indices) if uv_indices else 5
    else:
        uv_max = 5
    if uv_max <= 2:
        uv_str = '低'
    elif uv_max <= 5:
        uv_str = '中等'
    elif uv_max <= 7:
        uv_str = '高'
    elif uv_max <= 10:
        uv_str = '極高'
    else:
        uv_str = '危險'

    # Visibility (current average)
    if hourly:
        visibilities = []
        for i, hour_time in enumerate(hourly.get('time', [])):
            if hour_time.startswith(date):
                vis = hourly.get('visibility', [])[i]
                if vis is not None:
                    visibilities.append(vis)
        avg_vis = sum(visibilities) / len(visibilities) if visibilities else 10000
    else:
        avg_vis = 10000

    if avg_vis > 10000:
        vis_str = '良好'
    elif avg_vis > 5000:
        vis_str = '尚可'
    else:
        vis_str = '較差'

    return {
        'date': date,
        'temp_max': round(temp_max_list[0]) if temp_max_list else temp_current,
        'temp_min': round(temp_min_list[0]) if temp_min_list else temp_current,
        'temp_current': temp_current,
        'icon': icon,
        'desc': desc,
        'humidity': humidity_str,
        'wind': wind_str,
        'uv': uv_str,
        'visibility': vis_str,
        'forecast': forecast,
    }


if __name__ == "__main__":
    print("=== Weather Fetcher Test ===\n")
    w = fetch_weather()
    for k, v in w.items():
        print(f"  {k}: {v}")
