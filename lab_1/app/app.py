import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import pdfkit
import tempfile
from ydata_profiling import ProfileReport
import seaborn as sns
sns.set_theme(style="darkgrid")

st.title("Analiza Interactivă a Energiei")

# df = pd.read_csv("../datasets/data.csv")


BASE_URL = "https://sistemulenergetic.ro/statistics/export/"
TIPURI_ENERGIE = [
    'carbune',
    'hidro',
    'hidrocarburi',
    'nuclear',
    'eolian',
    'fotovolt',
    'biomasa'
]


today = datetime.datetime.now()
prev_year = today.year - 1

date_range = st.sidebar.date_input(
    "Select your vacation for next year",
    (datetime.date(prev_year, 1, 1), today),
    format="MM.DD.YYYY",
)
selected = st.sidebar.multiselect(
    "Selectati tipul de energie",
    TIPURI_ENERGIE,
    default=TIPURI_ENERGIE,
)

start_date, end_date = date_range

# Attach times (you can change these if needed)
start_dt = datetime.datetime.combine(start_date, datetime.time(0, 0))
end_dt = datetime.datetime.combine(end_date, datetime.time(23, 59))


def to_path(dt: datetime.datetime) -> str:
    return dt.strftime("%Y/%m/%d/%H/%M")


date_path = f"{to_path(start_dt)}/{to_path(end_dt)}"

df = pd.read_csv(BASE_URL + date_path)
df.date = pd.to_datetime(df.date, errors="coerce")
df["an"] = df.date.dt.year
df["luna"] = df.date.dt.month
df["zi"] = df.date.dt.day
df["ora"] = df.date.dt.hour
df["minute"] = df.date.dt.minute
df["ziSapt"] = df.date.dt.weekday


columns = df.columns
filterd_colums = []
for col in columns:
    if col in TIPURI_ENERGIE:
        if col in selected:
            filterd_colums.append(col)
    else:
        filterd_colums.append(col)

st.text("Datele pentru perioada selectata")
df[filterd_colums]

st.text("Date aggregate")
if selected:
    aggs = df[selected].agg(["min", "max", "sum", "mean", "median", "std"])
    aggs.T

# Analiza corelatiilor (heatmap)
df_clean = df.copy()

# eliminam valorile negative
df_clean[selected] = df_clean[selected].clip(lower=0)

# agregare dupa ore
hour_order = list(range(24))
cols = selected
heat_data = (
    df_clean.groupby("ora")[cols]
    .mean()
    .reindex(hour_order)
    .T
)

labels = heat_data.round(0).astype(int).astype(str) + "\n" \
    " (" + (100*heat_data.div(heat_data.max(axis=1), axis=0)).round(0).astype(int).astype(str) + "%)"

# heatmap cu valori absolute (MW)
fig, ax = plt.subplots(figsize=(15, 8))
sns.heatmap(
    heat_data,
    annot=labels,
    fmt="",
    annot_kws={"size": 8},
    cmap="YlOrRd",
    linewidths=0.2,
    cbar_kws={"label": "Media pe ora (MW)"},
    ax=ax,
)
plt.title("Profil orar mediu pe tipuri de energie")
plt.xlabel("Ora")
plt.ylabel("Tip energie")
plt.tight_layout()

st.pyplot(fig)

# agregare dupa luni
months_order = sorted(df_clean["luna"].unique().tolist())

heat_data = (
    df_clean.groupby("luna")[selected]
    .mean()
    .reindex(months_order)
    .T
)

labels = heat_data.round(0).astype(int).astype(str) + "\n" \
    " (" + (100*heat_data.div(heat_data.max(axis=1), axis=0)).round(0).astype(int).astype(str) + "%)"

# heatmap cu valori absolute (MW)
fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(
    heat_data,
    annot=labels,
    fmt="",
    annot_kws={"size": 8},
    cmap="YlOrRd",
    linewidths=0.3,
    cbar_kws={"label": "Media pe luna (MW)"},
    ax=ax,
)
plt.title("Profil lunar mediu pe tipuri de energie")
plt.xlabel("Luna")
plt.ylabel("Tip energie")
plt.tight_layout()
st.pyplot(fig)

# Aggregarea dupa luni

monthly = (
    df
    .groupby(['an', 'luna'], as_index=False)[selected]
    .sum()
    .sort_values(['an', 'luna'])
)

# etichetă de tip "2025-08" pentru axa X
monthly['year_month'] = (monthly['an'].astype(str) + '-' + monthly['luna'].astype(str).str.zfill(2))

monthly_melt = monthly.melt(
    id_vars=['an', 'luna', 'year_month'],
    value_vars=selected,
    var_name='tip',
    value_name='productie'
)

fig = px.line(
    monthly_melt,
    x='year_month',
    y='productie',
    color='tip',
    markers=True,
    title='Producția lunară pe tipuri',
    labels={'year_month': 'Lună', 'productie': 'Producție', 'tip': 'Tip producție'}
)

fig.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig)

if st.sidebar.button("Generează raport PDF"):
    with st.spinner("Generez raportul..."):
        profile = ProfileReport(
            df,
            title="Profil date energie",
            explorative=True,
            minimal=True
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_html:
            tmp_html.write(profile.to_html())
            html_path = tmp_html.name

        pdf_path = html_path.replace('.html', '.pdf')
        pdfkit.from_file(html_path, pdf_path)

        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()

    st.sidebar.success("Raport PDF generat!")

    st.sidebar.download_button(
        label="📥 Descarcă raport PDF",
        data=pdf_data,
        file_name=f"raport_energie_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
