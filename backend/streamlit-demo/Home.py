import streamlit as st

from prism.common.log import Log

Log.init()

st.set_page_config(page_title="prism", layout="wide")

st.header(f"X Trending Analysis", divider='rainbow')

user_msg = {
    "name": "user",
    "avatar": '🧑‍💻',
}

if user_input := st.chat_input('Enter Trending Keyword:'):
    with st.chat_message(**user_msg):
        st.write(user_input)
