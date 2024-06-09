import streamlit as st
import pandas as pd
import streamlit as st

from datetime import datetime, time
import io
import json

import base64
from pathlib import Path



# subtitles
def subtitle(content, color="black", text_align="left", font_size="30px"):

    st.markdown(f'''<div style="font-family:'DM Sans', sans-serif, avenir; font-size:{font_size}; font-weight:bold; color:{color}; text-align:{text_align};">{content}</div>''',unsafe_allow_html=True)


# titles
def title(content, color="black", text_align="left", font_size="50px"):
    st.markdown(f'''<div style="font-family:'DM Sans', sans-serif, avenir; font-size:{font_size}; font-weight:bold; color:{color}; text-align:{text_align};">{content}</div>''',unsafe_allow_html=True)


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded


def img_to_html(img_path, img_alt):
    img_format = img_path.split(".")[-1]
    img_html = f'<img src="data:image/{img_format.lower()};base64,{img_to_bytes(img_path)}" alt="{img_alt}" style="max-width: 100%;">'

    return img_html
