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

# ฟังก์ชันกรองข้อมูลแนะนำ
def get_suggestions(column, keyword):
    return data[data[column].str.contains(keyword, na=False)][column].unique()

# สร้าง UI ใน Streamlit
st.title("กรอกข้อมูลสำหรับการทำนาย")

# รับข้อมูลจากผู้ใช้พร้อมการแนะนำ
name = st.text_input("ชื่อ")
address = st.text_input("ที่อยู่")

# ฟิลด์ แขวง/ตำบล พร้อมการแนะนำ
suggestions = list(get_suggestions("TambonThai", sub_district_input)) if sub_district_input else []
sub_district = st.selectbox("เลือกแขวง/ตำบล", options=suggestions) if suggestions else sub_district_input

# ฟิลด์ เขต/อำเภอ พร้อมการแนะนำ
suggestions = list(get_suggestions("DistrictThai", district_input)) if district_input else []
district = st.selectbox("เลือกเขต/อำเภอ", options=suggestions) if suggestions else district_input

# ฟิลด์ จังหวัด พร้อมการแนะนำ
suggestions = list(get_suggestions("ProvinceThai", province_input)) if province_input else []
province = st.selectbox("เลือกจังหวัด", options=suggestions) if suggestions else province_input

# ฟิลด์ รหัสไปรษณีย์ จะทำการแนะนำรหัสที่ตรงกัน
if sub_district and district and province:
    postal_codes = data[
        (data["TambonThai"] == sub_district) &
        (data["DistrictThai"] == district) &
        (data["ProvinceThai"] == province)
    ]["PostCodeMain"].unique()
    postal_code = st.selectbox("รหัสไปรษณีย์", options=postal_codes) if postal_codes.size > 0 else st.text_input("รหัสไปรษณีย์")
else:
    postal_code = st.text_input("รหัสไปรษณีย์")

# เมื่อผู้ใช้กดปุ่มให้ทำการทำนาย
if st.button("ทำนาย"):
    # รวมข้อมูลทั้งหมดเป็นข้อความเดียว
    user_input = f"{name} {sub_district} {district} {province} {postal_code}"
    
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
