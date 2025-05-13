import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os
import random
from datetime import datetime

# --- 設定 ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# --- ファイルパス ---
tasks_file = "tasks.csv"
responses_file = "responses.csv"

# --- 初期ファイル作成（カラムあり） ---
if not os.path.exists(responses_file) or os.path.getsize(responses_file) == 0:
    pd.DataFrame(columns=["timestamp", "task", "answer", "feedback", "likes"]).to_csv(responses_file, index=False)

# --- タスク読み込み ---
tasks_df = pd.read_csv(tasks_file)

# --- ページ切り替え ---
page = st.sidebar.radio("ページを選択", ["暇つぶし手伝い", "回答一覧"])

# --- ページ1: 暇つぶし手伝い ---
if page == "暇つぶし手伝い":
    st.title("🙋 暇つぶし手伝いアプリ")

    if "task" not in st.session_state:
        st.session_state.task = None

    if st.button("困ってる人のタスクを見る"):
        selected_row = tasks_df.sample(1).iloc[0]
        st.session_state.task = selected_row["task_description"]
        st.info(f"📩 お題: {st.session_state.task}")

    if st.session_state.task:
        user_answer = st.text_area("📝 あなたの回答")

        if st.button("手伝う！"):
            if not user_answer.strip():
                st.warning("回答を入力してください")
            else:
                with st.spinner("OpenAIがフィードバック生成中..."):
                    try:
                        feedback_prompt = f"以下の回答に対して感謝のコメントをください:\n\n{user_answer}"
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": feedback_prompt}],
                            temperature=0.7,
                        )
                        feedback = response.choices[0].message.content
                        likes = random.randint(10, 1000)

                        # 表示
                        st.success("✅ 手伝い完了！")
                        st.markdown(f"🗨️ フィードバック: {feedback}")
                        st.metric(label="❤️ いいね数", value=f"{likes}件")

                        # 回答保存
                        new_row = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "task": st.session_state.task,
                            "answer": user_answer,
                            "feedback": feedback,
                            "likes": likes
                        }
                        pd.concat([pd.read_csv(responses_file), pd.DataFrame([new_row])]).to_csv(responses_file, index=False)

                        # タスクリセット
                        st.session_state.task = None

                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")

# --- ページ2: 回答一覧 ---
else:
    st.title("📊 回答一覧")

    try:
        df_responses = pd.read_csv(responses_file)

        if df_responses.empty:
            st.info("まだ回答がありません")
        else:
            st.write(f"📝 これまでの回答：{len(df_responses)}件")

            # フィルター（お題別）
            task_options = ["全て"] + df_responses["task"].unique().tolist()
            selected_task = st.selectbox("お題で絞り込み", task_options)

            if selected_task != "全て":
                df_responses = df_responses[df_responses["task"] == selected_task]

            st.dataframe(df_responses, use_container_width=True)

            # --- 回答数推移グラフ ---
            st.subheader("🗓️ 回答数の推移")

            df_responses["timestamp"] = pd.to_datetime(df_responses["timestamp"], errors="coerce")
            df_responses = df_responses.dropna(subset=["timestamp"])  # timestampがNaTなら削除

            if not df_responses.empty:
                df_responses["date"] = df_responses["timestamp"].dt.date
                daily_counts = df_responses.groupby("date").size()

                st.bar_chart(daily_counts)
            else:
                st.info("有効な日時データがありません")

            # --- 人気お題ランキング ---
            st.subheader("🏆 人気お題ランキング")

            top_tasks = df_responses["task"].value_counts().head(5)

            if not top_tasks.empty:
                st.bar_chart(top_tasks)
            else:
                st.info("お題別の回答データがありません")

    except pd.errors.EmptyDataError:
        st.info("まだ回答がありません（ファイルは存在しますが中身が空です）")

# # --- ページ2: 回答一覧 ---
# else:
#     st.title("📊 回答一覧")

#     try:
#         df_responses = pd.read_csv(responses_file)

#         if df_responses.empty:
#             st.info("まだ回答がありません")
#         else:
#             st.write(f"📝 これまでの回答：{len(df_responses)}件")

#             # フィルター（お題別）
#             task_options = ["全て"] + df_responses["task"].unique().tolist()
#             selected_task = st.selectbox("お題で絞り込み", task_options)

#             if selected_task != "全て":
#                 df_responses = df_responses[df_responses["task"] == selected_task]

#             st.dataframe(df_responses, use_container_width=True)

#     except pd.errors.EmptyDataError:
#         st.info("まだ回答がありません（ファイルは存在しますが中身が空です）")
