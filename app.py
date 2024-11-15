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
st.title("กรอกข้อมูลสำหรับการทำนาย")

# เลือกจังหวัด
province_options = data["ProvinceThai"].unique()
province = st.selectbox("เลือกจังหวัด", options=province_options)

# เลือกเขต/อำเภอ โดยกรองจากจังหวัดที่เลือก
district_options = data[data["ProvinceThai"] == province]["DistrictThai"].unique()
district = st.selectbox("เลือกเขต/อำเภอ", options=district_options)

# เลือกแขวง/ตำบล โดยกรองจากเขต/อำเภอและจังหวัดที่เลือก
sub_district_options = data[(data["ProvinceThai"] == province) & (data["DistrictThai"] == district)]["TambonThai"].unique()
sub_district = st.selectbox("เลือกแขวง/ตำบล", options=sub_district_options)

# รหัสไปรษณีย์โดยอัตโนมัติจากแขวง/ตำบล, เขต/อำเภอ และจังหวัดที่เลือก
postal_codes = data[(data["ProvinceThai"] == province) & 
                    (data["DistrictThai"] == district) & 
                    (data["TambonThai"] == sub_district)]["PostCodeMain"].unique()
postal_code = postal_codes[0] if postal_codes.size > 0 else "ไม่พบรหัสไปรษณีย์"

st.write("รหัสไปรษณีย์:", postal_code)

# เมื่อผู้ใช้กดปุ่มให้ทำการทำนาย
if st.button("ทำนาย"):
    # รวมข้อมูลทั้งหมดเป็นข้อความเดียว
    user_input = f"{province} {district} {sub_district} {postal_code}"
    
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
