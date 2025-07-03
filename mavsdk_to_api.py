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
            print(" Kết nối thành công với drone!")
            break

    while True:
        try:
            battery = await drone.telemetry.battery().__anext__()
            position = await drone.telemetry.position().__anext__()
            in_flight = await drone.telemetry.in_air().__anext__()
            velocity = await drone.telemetry.velocity_ned().__anext__()
            heading = await drone.telemetry.heading().__anext__()
            health = await drone.telemetry.health().__anext__()
            is_armed = await drone.telemetry.armed().__anext__()
            flight_mode = await drone.telemetry.flight_mode().__anext__()

            battery_percent = round(battery.remaining_percent * 100, 2)
            latitude = round(position.latitude_deg, 6)
            longitude = round(position.longitude_deg, 6)
            altitude = round(position.relative_altitude_m, 2)
            ground_speed = round((velocity.north_m_s**2 + velocity.east_m_s**2)**0.5, 2)
            heading_deg = round(heading.heading_deg, 2)

            print(f"🔋 {battery_percent}% | 📍 {latitude}, {longitude}, Alt: {altitude}m | "
                  f"🧭 Heading: {heading_deg}° | 💨 GS: {ground_speed} m/s | "
                  f"✈️ InFlight: {in_flight} | 🛡️ Armed: {is_armed} | 🧠 Mode: {flight_mode}")

            # Gửi dữ liệu tới Flask API
            response = requests.post(API_URL, json={
                "battery_level": battery_percent,
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "ground_speed": ground_speed,
                "heading": heading_deg,
                "in_flight": in_flight,
                "is_armed": is_armed,
                "flight_mode": str(flight_mode)
            })

            if response.status_code == 201:
                print(" Gửi dữ liệu thành công.")
            else:
                print(f" Lỗi gửi API: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"⚠️ Lỗi: {e}")

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run())
