import utils
import os


current_file_name = os.path.splitext(os.path.basename(__file__))[0]+".md"
page_title = "yet another local GPT"
utils.init_page(current_file_name, page_title, allow_html=True)
