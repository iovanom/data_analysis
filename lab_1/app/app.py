import streamlit as st
import pandas as pd
import numpy as np
import time

st.title("Laborator 1")

# df = pd.read_csv("../datasets/data.csv")

df = pd.read_csv("https://sistemulenergetic.ro/statistics/export/2022/10/09/23/59/2025/10/09/23/59")
df

left_column, right_column = st.columns(2)

with left_column:
    # st.write(df)
    #st.dataframe(df.style.highlight_max(axis=0))
    st.write("one column")

energ = st.sidebar.selectbox("Selectati tipul de energie", df.columns[1:])

with right_column:
    st.write("two column")

data = df[["date", energ]]
data
st.line_chart(df[["date", energ]], x="date")
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"]
)

st.map(map_data)

x = st.slider('x')
st.write(x, 'squared is', x * x)

st.text_input("Your name", key="name")

# You can access the value at any point with:
st.session_state.name

if st.checkbox('Show dataframe'):
    "Starting a long computation..."
    latest_iteration = st.empty()
    bar = st.progress(0)
    for i in range(100):
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)
    "...and now we're done!"

