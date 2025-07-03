import asyncio
from mavsdk import System

async def run():
    
    lat = float(input("🌐 Nhập Latitude: "))
    lon = float(input("🌐 Nhập Longitude: "))
    alt = float(input("🛫 Nhập Altitude (MSL): "))

    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("🔌 Đang kết nối đến drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(" Đã kết nối!")
            break

    

    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(5)  

    print(f" flight ({lat}, {lon}, {alt})...")
    await drone.action.goto_location(lat, lon, alt, 0.0)

    
    await asyncio.sleep(10)

    # Hạ cánh
    print("hạ cánh.")
    await drone.action.land()

if __name__ == "__main__":
    asyncio.run(run())
