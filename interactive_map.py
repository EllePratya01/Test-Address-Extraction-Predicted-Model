import streamlit as st
import pydeck as pdk
import pandas as pd

# ข้อมูลตำแหน่งศูนย์กลางของประเทศไทย
thailand_lat = 13.736717
thailand_lon = 100.523186

# สร้าง DataFrame ตัวอย่างข้อมูลสถานที่ในประเทศไทย (หรือใช้ข้อมูลจริงของคุณเอง)
data = pd.DataFrame({
    'lat': [13.736717, 13.756331, 13.689999],
    'lon': [100.523186, 100.501762, 100.750112],
    'name': ['Bangkok', 'Bangkok Riverside', 'Nonthaburi']
})

# กำหนดค่าเริ่มต้นสำหรับแผนที่
view_state = pdk.ViewState(
    latitude=thailand_lat,
    longitude=thailand_lon,
    zoom=6,
    pitch=50
)

# สร้างเลเยอร์สำหรับแสดงจุดข้อมูล
layer = pdk.Layer(
    'ScatterplotLayer',
    data=data,
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=20000,
    pickable=True
)

# สร้างแผนที่
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{name}"}
)

# แสดงแผนที่ใน Streamlit
st.title("Interactive Map of Thailand")
st.pydeck_chart(r)
