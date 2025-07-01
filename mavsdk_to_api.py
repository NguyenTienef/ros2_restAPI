import asyncio
from mavsdk import System
import requests

API_URL = "http://localhost:5000/api/telemetry"

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("🔌 Đang kết nối tới drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("✅ Kết nối thành công với drone!")
            break

    while True:
        try:
            battery = await drone.telemetry.battery().__anext__()
            position = await drone.telemetry.position().__anext__()
            in_flight = await drone.telemetry.in_air().__anext__()

            battery_percent = round(battery.remaining_percent * 100, 2)
            latitude = round(position.latitude_deg, 6)
            longitude = round(position.longitude_deg, 6)
            altitude = round(position.relative_altitude_m, 2)

            print(f"🔋 Battery: {battery_percent}% | "
                  f"📍 Lat: {latitude}, Lon: {longitude}, Alt: {altitude} | "
                  f"✈️ In Flight: {in_flight}")

            response = requests.post(API_URL, json={
                "battery_level": battery_percent,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "in_flight": in_flight
            })

            if response.status_code == 201:
                print("✅ Gửi dữ liệu thành công.")
            else:
                print(f"❌ Lỗi gửi API: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"⚠️ Lỗi: {e}")

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
