import streamlit as st
import joblib
import pandas as pd
import sklearn_crfsuite

# โหลดข้อมูลจากไฟล์ Excel
data = pd.read_excel("thaidata.xlsx")

# โหลดโมเดล
model = joblib.load("model.joblib")

# รายการคำหยุด
stopwords = ["ผู้", "ที่", "ซึ่ง", "อัน"]

# ฟังก์ชันสร้างคุณสมบัติจากโทเค็น
def tokens_to_features(tokens, i):
    word = tokens[i]
    features = {
        "bias": 1.0,
        "word.word": word,
        "word[:3]": word[:3],
        "word.isspace()": word.isspace(),
        "word.is_stopword()": word in stopwords,
        "word.isdigit()": word.isdigit(),
        "word.islen5": word.isdigit() and len(word) == 5
    }
    if i > 0:
        prevword = tokens[i - 1]
        features.update({
            "-1.word.prevword": prevword,
            "-1.word.isspace()": prevword.isspace(),
            "-1.word.is_stopword()": prevword in stopwords,
            "-1.word.isdigit()": prevword.isdigit(),
        })
    else:
        features["BOS"] = True

    if i < len(tokens) - 1:
        nextword = tokens[i + 1]
        features.update({
            "+1.word.nextword": nextword,
            "+1.word.isspace()": nextword.isspace(),
            "+1.word.is_stopword()": nextword in stopwords,
            "+1.word.isdigit()": nextword.isdigit(),
        })
    else:
        features["EOS"] = True

    return features

# ฟังก์ชันสำหรับทำนาย
def predict(text):
    tokens = text.split()
    features = [tokens_to_features(tokens, i) for i in range(len(tokens))]
    return model.predict([features])[0], tokens  # Return both predictions and tokens

# สร้าง UI ใน Streamlit
st.markdown("<h2 style='text-align: center; font-size: 28px;'>Address Extraction Predicted Model</h2>", unsafe_allow_html=True)

# รับข้อมูลจากผู้ใช้
name = st.text_input("ชื่อ (Name)")
address = st.text_input("ที่อยู่ (Address)")

# เลือกแขวง/ตำบล โดยมีตัวเลือกเริ่มต้นเป็นช่องว่าง
sub_district = st.selectbox(
    "เลือกแขวง/ตำบล (Sub-District)",
    options=[""] + sorted(data["TambonThaiShort"].unique())
)

# เลือกเขต/อำเภอ โดยกรองจากแขวง/ตำบลที่เลือกและมีตัวเลือกเริ่มต้นเป็นช่องว่าง
district_options = sorted(data[data["TambonThaiShort"] == sub_district]["DistrictThaiShort"].unique()) if sub_district else []
district = st.selectbox("เลือกเขต/อำเภอ (District)", options=[""] + district_options)

# เลือกจังหวัด โดยกรองจากเขต/อำเภอและแขวง/ตำบลที่เลือกและมีตัวเลือกเริ่มต้นเป็นช่องว่าง
province_options = sorted(data[(data["TambonThaiShort"] == sub_district) & (data["DistrictThaiShort"] == district)]["ProvinceThai"].unique()) if district else []
province = st.selectbox("เลือกจังหวัด (Province)", options=[""] + province_options)

# รหัสไปรษณีย์โดยอัตโนมัติจากแขวง/ตำบล, เขต/อำเภอ และจังหวัดที่เลือก
postal_codes = data[(data["ProvinceThai"] == province) & 
                    (data["DistrictThaiShort"] == district) & 
                    (data["TambonThaiShort"] == sub_district)]["PostCodeMain"].unique()
postal_code = postal_codes[0] if postal_codes.size > 0 else "ไม่พบรหัสไปรษณีย์"

st.write("รหัสไปรษณีย์ (Postal Code):", postal_code)

# เมื่อผู้ใช้กดปุ่มให้ทำการทำนาย
if st.button("ทำนาย"):
    # รวมข้อมูลทั้งหมดเป็นข้อความเดียว
    user_input = f"{name} {address} {sub_district} {district} {province} {postal_code}"
    
    # ทำนายผลลัพธ์จากโมเดล
    predictions, tokens = predict(user_input)
    
    # สร้าง DataFrame สำหรับการแสดงผล
    results_df = pd.DataFrame({
        "คำที่ผู้ใช้กรอก": tokens,
        "ผลการทำนาย": predictions
    })

    # แสดงผลลัพธ์การทำนาย
    st.write("ผลการทำนาย:")
    st.dataframe(results_df.T)  # ใช้ .T เพื่อแสดงในแนวนอน
