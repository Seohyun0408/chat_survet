import streamlit as st
import openai
import pandas as pd

# ✅ OpenAI API 키 입력
openai.api_key = "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"  # OpenAI 계정에서 발급받은 키

# 🧓 타이틀
st.title("소프트웨어 제품 사용자 설문")

# ------------------------
# 📊 정량 설문 (Likert)
# ------------------------
likert_questions = [
    "1. 이 앱의 메뉴와 기능 배치는 이해하기 쉬웠습니까?",
    "2. 글씨 크기, 색상 등 화면의 시각적 구성이 편안하게 느껴졌습니까?",
    "3. 원하는 기능을 찾고 사용하는 과정이 간단했습니까?",
    "4. 인증, 검색, 예약 등의 절차에서 혼란을 느낀 적이 있었습니까?",
    "5. 이 앱은 시니어를 위한 서비스라고 느껴졌습니까?",
    "6. 일상 속에서 지속적으로 사용할 가치가 있다고 느꼈습니까?"
]
choices = ["1 (전혀 아니다)", "2", "3", "4", "5 (매우 그렇다)"]

st.header("📊 정량 설문 (5점 척도)")
likert_answers = []
for q in likert_questions:
    likert_answers.append(st.selectbox(q, choices, key=q))

# ------------------------
# 💬 정성 대화형 설문
# ------------------------
open_questions = [
    "1. 처음 앱을 사용했을 때 가장 어려웠던 점은 무엇이었습니까?",
    "2. 특정 기능을 사용할 때 당황하거나 다시 돌아간 적이 있습니까?",
    "3. 이 앱이 시니어 사용자를 고려했다고 느낀 부분이 있습니까?",
    "4. 이 앱이 평소 생활에서 어떤 상황에 가장 유용할 것 같습니까?"
]

st.header("💬 정성 설문")

# 🔁 GPT 꼬리질문 생성 함수
def generate_follow_up(original_question, user_response):
    prompt = f"""
    다음은 사용자 설문 응답입니다.
    질문: "{original_question}"
    응답: "{user_response}"

    사용자의 응답이 짧거나 모호한 경우, 명확히 하기 위한 꼬리질문을 하나 작성해 주세요.
    사용자 응답이 충분히 구체적이면 "없음"이라고만 답변하세요.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        follow_up = response.choices[0].message.content.strip()
        return follow_up
    except Exception as e:
        return f"GPT 오류: {e}"

# 🔧 세션 상태 초기화
if "qa_pairs" not in st.session_state:
    st.session_state.qa_pairs = []
if "step" not in st.session_state:
    st.session_state.step = 0
if "follow_up_active" not in st.session_state:
    st.session_state.follow_up_active = False
if "follow_up_question" not in st.session_state:
    st.session_state.follow_up_question = ""

# ▶️ 질문 진행
if st.session_state.step < len(open_questions):
    q = open_questions[st.session_state.step]

    # 📍 메인 질문
    if not st.session_state.follow_up_active:
        st.markdown(f"**질문:** {q}")
        ans = st.text_input("답변을 입력하세요:", key=f"q{st.session_state.step}")
        if st.button("답변 제출", key=f"submit{st.session_state.step}"):
            follow_up = generate_follow_up(q, ans)
            if follow_up.lower() != "없음":
                st.session_state.qa_pairs.append((q, ans))
                st.session_state.follow_up_question = follow_up
                st.session_state.follow_up_active = True
                st.rerun()
            else:
                st.session_state.qa_pairs.append((q, ans))
                st.session_state.step += 1
                st.rerun()

    # 📍 꼬리질문
    else:
        st.markdown(f"**꼬리질문:** {st.session_state.follow_up_question}")
        f_ans = st.text_input("추가 답변을 입력하세요:", key=f"fup{st.session_state.step}")
        if st.button("꼬리답변 제출", key=f"fsubmit{st.session_state.step}"):
            st.session_state.qa_pairs.append((st.session_state.follow_up_question, f_ans))
            st.session_state.follow_up_active = False
            st.session_state.follow_up_question = ""
            st.session_state.step += 1
            st.rerun()

# ✅ 모든 질문 완료 후 결과 요약
else:
    st.success("설문이 완료되었습니다. 감사합니다!")

    df_likert = pd.DataFrame({
        "질문": likert_questions,
        "응답": likert_answers
    })
    df_open = pd.DataFrame(st.session_state.qa_pairs, columns=["질문", "응답"])

    st.markdown("### 정량 설문 결과")
    st.dataframe(df_likert)

    st.markdown("### 정성 설문 결과")
    st.dataframe(df_open)

    # 다운로드 버튼
    csv_open = df_open.to_csv(index=False).encode("utf-8")
    st.download_button("📥 정성 설문 결과 다운로드", data=csv_open, file_name="open_survey.csv", mime="text/csv")

    csv_likert = df_likert.to_csv(index=False).encode("utf-8")
    st.download_button("📥 정량 설문 결과 다운로드", data=csv_likert, file_name="likert_survey.csv", mime="text/csv")

