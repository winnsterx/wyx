import streamlit as st
import os

# st.write("hello world")

posts = []
posts_path = "./posts"
files = os.listdir(posts_path)
for file in files:
    with open(os.path.join(posts_path, file), 'r') as f:
        content = f.read()
        posts.append(content)
print(posts)

st.markdown(posts[0])
