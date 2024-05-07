import utils
import os
import streamlit as st

current_file_name = os.path.splitext(os.path.basename(__file__))[0]+".md"
page_title = "about me"
utils.init_page(current_file_name, page_title)
