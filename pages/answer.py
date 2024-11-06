import streamlit as st
import pandas as pd

# CSV 파일에서 데이터 불러오기
try:
    answers_df = pd.read_csv('answers.csv')
    st.write("데이터 로드 확인:", answers_df.head())  # CSV 파일의 일부 데이터를 출력하여 확인
except FileNotFoundError:
    st.error("answers.csv 파일이 서버에 없습니다. 먼저 업로드 페이지에서 파일을 업로드하세요.")
    st.stop()

st.title("학생 엑셀 채점 시스템")

# 'all_submitted' 상태 초기화
if "all_submitted" not in st.session_state:
    st.session_state["all_submitted"] = False

# 연도 및 월 필터링 옵션 추가
unique_years = sorted(answers_df['연도'].unique())
selected_year = st.selectbox("연도를 선택하세요", unique_years)

filtered_months = sorted(answers_df[answers_df['연도'] == selected_year]['월'].unique())
selected_month = st.selectbox("월을 선택하세요", filtered_months)

# 선택한 연도와 월에 맞는 문제 필터링
filtered_questions = answers_df[(answers_df['연도'] == selected_year) & (answers_df['월'] == selected_month)]

# 안내 메시지
st.header(f"{selected_year}년 {selected_month}월 모의고사 문제")
st.subheader("정답은 1-5 사이의 숫자 중 하나를 선택해주세요.")

# 학생 답안 입력 섹션
check_results = {}

# 문제를 한 줄에 한 문제씩 출력
for index, row in filtered_questions.iterrows():
    question_num = row['번호']  # D열: 문제 번호
    correct_answer = row['정답']  # A열: 정답
    question_type = row['유형']  # F열: 문제 유형
    descriptive_text = str(row['서술형']).replace("\\r\\n", "\n") if pd.notna(row['서술형']) else ""  # G열: 서술형에서 \r\n을 줄바꿈으로 변환

    # 개별 문제 제출 상태 관리
    if f"submitted_{question_num}" not in st.session_state:
        st.session_state[f"submitted_{question_num}"] = False

    # 컬럼을 사용해 문제 번호, 라디오 버튼, 결과 표시를 나란히 배치
    cols = st.columns([1, 4, 1])  # 3개의 컬럼 (문제 번호 + 유형, 보기, 결과)
    
    with cols[0]:
        st.write(f"{question_num}번 - {question_type}")  # 문제 번호와 문제 유형 표시

    with cols[1]:
        # 문제 번호와 라디오 버튼을 한 줄에 표시 (기본 선택 없음)
        student_answer = st.radio(
            f"문제 {question_num}",
            options=[None, 1, 2, 3, 4, 5],  # None을 추가하여 기본 선택 없음
            format_func=lambda x: "" if x is None else str(x),  # None일 경우 빈 문자열로 표시
            key=f"answer_{question_num}",
            horizontal=True,
            label_visibility="collapsed"
        )

# 제출 버튼
if st.button("제출"):
    # 모든 문제에 답이 입력된 경우 채점 수행
    for _, row in filtered_questions.iterrows():
        question_num = row['번호']
        correct_answer = row['정답']
        question_type = row['유형']  # F열: 문제 유형
        descriptive_text = str(row['서술형']).replace("\\r\\n", "\n") if pd.notna(row['서술형']) else ""  # NaN을 빈 문자열로 처리
        student_answer = st.session_state.get(f"answer_{question_num}", None)

        # 정답 확인 및 피드백 제공
        try:
            if int(student_answer) == int(correct_answer):  # 비교 전에 정수로 변환
                check_results[question_num] = (True, student_answer, question_type, descriptive_text)
            else:
                check_results[question_num] = (False, student_answer, question_type, descriptive_text)
        except ValueError:
            check_results[question_num] = (False, None, question_type, descriptive_text)

    # 각 문제 상태를 제출 완료로 설정
    st.session_state["all_submitted"] = True

# 전체 제출 결과 출력
for question_num, result in check_results.items():
    is_correct, selected_answer, question_type, descriptive_text = result
    cols = st.columns([1, 4, 1])  # 문제 번호, 보기, 결과 표시용 컬럼
    
    with cols[0]:
        st.write(f"{question_num}번 - {question_type}")  # 문제 번호와 유형 표시
    
    with cols[1]:
        # 라디오 버튼 표시 (답안 입력 후 표시를 위해 비활성화)
        st.radio(
            f"문제 {question_num}",
            options=[None, 1, 2, 3, 4, 5],
            index=selected_answer if selected_answer is not None else 0,
            format_func=lambda x: "" if x is None else str(x),
            key=f"disabled_answer_{question_num}",
            horizontal=True,
            disabled=True,
            label_visibility="collapsed"
        )

    with cols[2]:
        # 맞은 답과 틀린 답을 표시
        if is_correct:
            st.markdown("<span style='color: green; font-size: 1.5em;'>✅</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color: red; font-size: 1.5em;'>❌</span>", unsafe_allow_html=True)

    # 오답일 경우 해당 문제 바로 아래에 서술형 설명 출력
    if not is_correct:
        st.warning(f"오답 서술형: {descriptive_text}")
