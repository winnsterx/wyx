import os
import streamlit as st
posts_path = "./posts"


def init_page(current_file_name, allow_html=False):
    st.set_page_config(page_icon="🌞", page_title=None)
    with open(os.path.join(posts_path, current_file_name), 'r') as f:
        content = f.read()
        st.markdown(content, unsafe_allow_html=allow_html)
