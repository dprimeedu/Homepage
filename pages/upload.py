import streamlit as st
import pandas as pd

st.title("CSV 파일 업로드")

# 파일 업로드 섹션
uploaded_file = st.file_uploader("answers.csv 파일을 업로드하세요", type="csv")

if uploaded_file:
    # CSV 파일을 Pandas DataFrame으로 읽기
    answers_df = pd.read_csv(uploaded_file)
    
    # 서버에 파일 저장
    with open("answers.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("answers.csv 파일이 서버에 성공적으로 저장되었습니다.")
    
    # 저장된 데이터 전체 표시 (확인용)
    st.dataframe(answers_df)  # st.write 대신 st.dataframe 사용
else:
    st.info("answers.csv 파일을 업로드하세요.")
