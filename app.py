import streamlit as st
import joblib
import sklearn_crfsuite

# โหลดโมเดล
model = joblib.load("/mnt/data/model.joblib")

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
    return model.predict([features])[0]

# สร้าง UI ใน Streamlit
st.title("กรอกข้อมูลสำหรับการทำนาย")

# รับข้อมูลจากผู้ใช้
name = st.text_input("ชื่อ")
address = st.text_input("ที่อยู่")
sub_district = st.text_input("แขวง/ตำบล")
district = st.text_input("เขต/อำเภอ")
province = st.text_input("จังหวัด")
postal_code = st.text_input("รหัสไปรษณีย์")

# เมื่อผู้ใช้กดปุ่มให้ทำการทำนาย
if st.button("ทำนาย"):
    # รวมข้อมูลทั้งหมดเป็นข้อความเดียว
    user_input = f"{name} {address} {sub_district} {district} {province} {postal_code}"
    
    # ทำนายผลลัพธ์จากโมเดล
    prediction = predict(user_input)
    
    # แสดงผลลัพธ์การทำนาย
    st.write("ผลการทำนาย:")
    st.write(prediction)

streamlit run app.py
