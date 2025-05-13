import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# 環境変数読み込み
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# サイドバー
st.sidebar.title("OpenAI 設定")
model = st.sidebar.selectbox("モデルを選択", ["gpt-3.5-turbo", "gpt-4o"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

# メイン画面
st.title("📝 OpenAI API テンプレート")

# ユーザー入力
user_input = st.text_area("💬 プロンプトを入力してください", placeholder="例: この文章を要約して")

# ボタンでAPI実行
if st.button("実行！"):
    if not user_input.strip():
        st.warning("プロンプトを入力してください")
    else:
        with st.spinner("OpenAIに問い合わせ中..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": user_input}
                    ],
                    temperature=temperature,
                )
                result_text = response.choices[0].message.content
                st.success("✅ 生成結果")
                st.markdown(result_text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
