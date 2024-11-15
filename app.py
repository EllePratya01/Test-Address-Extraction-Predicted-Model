import streamlit as st
import joblib
import pandas as pd

# Load data and model
data = pd.read_excel("thaidata.xlsx")
model = joblib.load("model.joblib")

# Stopwords list
stopwords = ["ผู้", "ที่", "ซึ่ง", "อัน"]

# Feature extraction function
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

# Prediction function
def predict(text):
    tokens = text.split()
    features = [tokens_to_features(tokens, i) for i in range(len(tokens))]
    return model.predict([features])[0], tokens

# Streamlit UI
st.markdown("<h2 style='text-align: center; font-size: 28px;'>Address Extraction Predicted Model</h2>", unsafe_allow_html=True)

# User inputs
name = st.text_input("ชื่อ (Name)")
address = st.text_input("ที่อยู่ (Address)")

# Select options
sub_district = st.selectbox("เลือกแขวง/ตำบล (Sub-District)", options=[""] + sorted(data["TambonThaiShort"].unique()))
district_options = sorted(data[data["TambonThaiShort"] == sub_district]["DistrictThaiShort"].unique()) if sub_district else []
district = st.selectbox("เลือกเขต/อำเภอ (District)", options=[""] + district_options)
province_options = sorted(data[(data["TambonThaiShort"] == sub_district) & (data["DistrictThaiShort"] == district)]["ProvinceThai"].unique()) if district else []
province = st.selectbox("เลือกจังหวัด (Province)", options=[""] + province_options)

# Auto-fill postal code
postal_codes = data[(data["ProvinceThai"] == province) & (data["DistrictThaiShort"] == district) & (data["TambonThaiShort"] == sub_district)]["PostCodeMain"].unique()
postal_code = postal_codes[0] if postal_codes.size > 0 else "ไม่พบรหัสไปรษณีย์"
st.write("รหัสไปรษณีย์ (Postal Code):", postal_code)
