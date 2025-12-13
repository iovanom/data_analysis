import re
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sns.set_theme(style="whitegrid")


# ------------------------------------------------------------
# DATE & PREPROCESARE (identic cu notebook-ul, dar în funcții)
# ------------------------------------------------------------

@st.cache_data
def load_data(csv_path: str = "./datasets/wines_raw.csv") -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # quality_price = points / price
    df["quality_price"] = df["points"] / df["price"]

    # standardizare țări
    mapCountries = {
        "Bosnia - Herzegovina": "Bosnia and Herzegovina",
        "China": "China (Mainland)",
        "Macedonia": "North Macedonia",
        "Russia": "Russian Federation",
        "US": "United States",
        "USA": "United States",
    }
    df["country"] = df["country"].replace(mapCountries)

    # standardizare categorie
    mapCategory = {
        "Rosé": "Rose"
    }
    df["category"] = df["category"].replace(mapCategory)

    df["country"] = df["country"].astype("category")
    df["category"] = df["category"].astype("category")

    # scoatem outlierii pentru alcool
    df = df[(df['alcohol'] >= 5) & (df['alcohol'] <= 25)]

    # scoatem outlierii (1% – 99%) pentru price, points, quality_price
    numeric_cols = ['price', 'points', 'quality_price']
    q_low = df[numeric_cols].quantile(0.01)
    q_high = df[numeric_cols].quantile(0.99)
    mask = ((df[numeric_cols] >= q_low) & (df[numeric_cols] <= q_high)).all(axis=1)
    df_clean = df[mask].copy()

    return df_clean


@st.cache_resource
def get_stopwords():
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    stop_words = set(stopwords.words('english'))
    custom_stop = {
        'wine', 'wines', 'flavors', 'flavour', 'aromas', 'aroma',
        'drink', 'drinking', 'note', 'notes', 'finish',
        'palate', 'style', 'nose',
        'and', 'the', 'this'
    }
    stop_words |= custom_stop
    return stop_words


def simple_clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Zăâîșțöüéèóòçñãõüäöß\' ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@st.cache_data
def prepare_text_corpus(descriptions: pd.Series):
    """Curățăm descrierile și generăm tokeni + frecvențe globale."""
    stop_words = get_stopwords()
    descriptions = descriptions.fillna("").astype(str)
    descriptions_clean = descriptions.apply(simple_clean_text)

    all_tokens = []
    tokens_per_row = []

    for txt in descriptions_clean:
        tokens = word_tokenize(txt)
        tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
        all_tokens.extend(tokens)
        tokens_per_row.append(tokens)

    word_freq = Counter(all_tokens)

    return descriptions_clean, tokens_per_row, word_freq, all_tokens


@st.cache_resource
def build_tfidf_model(descriptions: pd.Series):
    """Construim TF-IDF pe descrieri pentru căutare text."""
    descriptions = descriptions.fillna("").astype(str)
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(descriptions)
    return vectorizer, tfidf_matrix


def search_wines(df: pd.DataFrame, query: str, top_n: int = 20) -> pd.DataFrame:
    """Caută vinuri după descriere folosind TF-IDF + cosine similarity."""
    if not query.strip():
        return pd.DataFrame()

    vectorizer, tfidf_matrix = build_tfidf_model(df["description"])
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
    idx = sims.argsort()[::-1][:top_n]
    results = df.iloc[idx].copy()
    results["similarity"] = sims[idx]
    return results


def compute_word_metric_summary(df: pd.DataFrame,
                                descriptions_clean: pd.Series,
                                max_candidates: int = 80,
                                min_freq: int = 100,
                                top_words: int = 15) -> pd.DataFrame:
    """Reproduce analiza de corelație cuvinte–metrice din notebook."""
    stop_words = get_stopwords()

    # tokenizare simplă per descriere (fără stopwords)
    tokens_per_row = descriptions_clean.apply(
        lambda x: [t for t in word_tokenize(x) if t.isalpha() and t not in stop_words]
    )

    word_freq = Counter()
    tokens_per_row.apply(word_freq.update)

    candidate_words = [
        w for (w, f) in word_freq.most_common(max_candidates)
        if f >= min_freq and len(w) > 3
    ][:top_words]

    # creăm coloane booleene word_<w>
    for w in candidate_words:
        pattern = rf'\b{re.escape(w)}\b'
        df[f'word_{w}'] = descriptions_clean.str.contains(pattern, regex=True)

    metrics = ['price', 'points', 'quality_price']
    rows = []

    for w in candidate_words:
        col = f'word_{w}'
        sub = df[[col] + metrics].dropna()
        present = sub[sub[col]]
        absent = sub[~sub[col]]

        row = {
            'word': w,
            'n_with': present.shape[0],
            'n_without': absent.shape[0],
            'frac_with': present.shape[0] / sub.shape[0]
        }
        for m in metrics:
            m_with = present[m].mean()
            m_without = absent[m].mean()
            row[f'{m}_with'] = m_with
            row[f'{m}_without'] = m_without
            row[f'{m}_diff'] = m_with - m_without

        rows.append(row)

    word_metric_summary = pd.DataFrame(rows).sort_values('points_diff', ascending=False)
    return word_metric_summary


# ------------------------------------------------------------
# FILTRARE
# ------------------------------------------------------------

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filtre")

    countries = sorted(df["country"].astype(str).unique())
    selected_countries = st.sidebar.multiselect(
        "Țări", countries, default=countries
    )

    categories = sorted(df["category"].astype(str).unique())
    selected_categories = st.sidebar.multiselect(
        "Categorii", categories, default=categories
    )

    min_price, max_price = float(df["price"].min()), float(df["price"].max())
    price_range = st.sidebar.slider(
        "Interval preț (USD)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=1.0
    )

    min_points, max_points = float(df["points"].min()), float(df["points"].max())
    points_range = st.sidebar.slider(
        "Punctaj (points)",
        min_value=min_points,
        max_value=max_points,
        value=(min_points, max_points),
        step=0.5
    )

    min_alc, max_alc = float(df["alcohol"].min()), float(df["alcohol"].max())
    alcohol_range = st.sidebar.slider(
        "Alcool (%)",
        min_value=min_alc,
        max_value=max_alc,
        value=(min_alc, max_alc),
        step=0.5
    )

    min_qp, max_qp = float(df["quality_price"].min()), float(df["quality_price"].max())
    qp_range = st.sidebar.slider(
        "Raport preț/calitate (quality_price)",
        min_value=min_qp,
        max_value=max_qp,
        value=(min_qp, max_qp),
        step=0.1
    )

    df_f = df[
        df["country"].astype(str).isin(selected_countries)
        & df["category"].astype(str).isin(selected_categories)
        & df["price"].between(price_range[0], price_range[1])
        & df["points"].between(points_range[0], points_range[1])
        & df["alcohol"].between(alcohol_range[0], alcohol_range[1])
        & df["quality_price"].between(qp_range[0], qp_range[1])
    ].copy()

    st.sidebar.markdown(f"**Număr vinuri după filtre:** {len(df_f)}")
    return df_f


# ------------------------------------------------------------
# TAB: OVERVIEW
# ------------------------------------------------------------

def tab_overview(df: pd.DataFrame):
    st.subheader("Overview general")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Număr vinuri", f"{len(df):,}".replace(",", " "))
    c2.metric("Preț mediu (USD)", f"{df['price'].mean():.2f}")
    c3.metric("Punctaj mediu", f"{df['points'].mean():.2f}")
    c4.metric("Quality_price mediu", f"{df['quality_price'].mean():.2f}")

    st.markdown("### Distribuția variabilelor numerice")

    numeric_cols = ['price', 'points', 'alcohol', 'quality_price']
    for col in numeric_cols:
        with st.expander(f"Distribuție {col}"):
            fig = px.histogram(
                df,
                x=col,
                nbins=50,
                marginal="box",
                title=f"Distribuția {col}",
            )
            fig.update_layout(
                bargap=0.05,
                xaxis_title=col,
                yaxis_title="Frecvență",
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Relații între variabile (scatter)")

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.scatter(
            df,
            x="price",
            y="points",
            color="category",
            hover_data=["country", "variety", "winery", "title"],
            opacity=0.4,
            title="Preț vs Punctaj (colorat după categorie)",
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.scatter(
            df,
            x="alcohol",
            y="points",
            color="category",
            hover_data=["country", "variety", "winery", "title"],
            opacity=0.4,
            title="Alcool vs Punctaj (colorat după categorie)",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Heatmap corelații (numerice)
    st.markdown("### Matricea de corelații (variabile numerice)")
    corr_matrix = df[["price", "points", "alcohol", "quality_price"]].corr()
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="Corelații între variabile numerice",
    )
    st.plotly_chart(fig_corr, use_container_width=True)


# ------------------------------------------------------------
# TAB: ȚĂRI & REGIUNI
# ------------------------------------------------------------

def tab_countries_regions(df: pd.DataFrame):
    st.subheader("Analiza pe țări și regiuni")

    dfc = df.copy()

    # număr de vinuri pe țară
    country_counts = dfc["country"].value_counts()

    # top țări după număr de vinuri
    top_n = st.number_input("Top N țări după număr vinuri", 5, 30, 10, step=1)
    top_country_counts = country_counts.head(top_n).reset_index()
    top_country_counts.columns = ["country", "count"]

    fig = px.bar(
        top_country_counts,
        x="country",
        y="count",
        title=f"Top {top_n} țări după numărul de vinuri",
        labels={"country": "Țară", "count": "Număr de vinuri"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # statistici medii pe țară
    country_stats = dfc.groupby("country", observed=False).agg(
        mean_price=("price", "mean"),
        mean_points=("points", "mean"),
        count=("country", "count"),
    ).reset_index()

    st.markdown("#### Scatter: preț mediu vs punctaj mediu pe țară")
    min_count = st.slider(
        "Minim număr de vinuri / țară pentru scatter",
        min_value=10,
        max_value=int(country_stats["count"].max()),
        value=30,
        step=5,
    )

    country_stats_f = country_stats[country_stats["count"] >= min_count]

    fig_sc = px.scatter(
        country_stats_f,
        x="mean_price",
        y="mean_points",
        size="count",
        color="mean_points",
        hover_name="country",
        title=f"Preț mediu vs Punctaj mediu pe țări (>= {min_count} vinuri)",
        labels={"mean_price": "Preț mediu", "mean_points": "Punctaj mediu"},
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # stacked bar: distribuția categoriilor pe țări
    st.markdown("#### Distribuția categoriilor de vin pe țări (stacked bar)")

    min_wines_country = st.slider(
        "Minim vinuri / țară pentru a fi inclusă în stacked bar",
        min_value=10,
        max_value=int(country_counts.max()),
        value=30,
        step=5,
    )
    valid_countries = country_counts[country_counts >= min_wines_country].index
    df_country_cat = dfc[dfc["country"].isin(valid_countries)].copy()

    ct_country_category = pd.crosstab(
        df_country_cat["country"], df_country_cat["category"]
    ).reset_index()

    ct_long = ct_country_category.melt(
        id_vars="country", var_name="category", value_name="count"
    )

    fig_stack = px.bar(
        ct_long,
        x="country",
        y="count",
        color="category",
        title=f"Distribuția vinurilor după categorii și țări (>= {min_wines_country} vinuri)",
        labels={"country": "Țară", "count": "Număr vinuri"},
    )
    fig_stack.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_stack, use_container_width=True)

    # stacked bar relativ (procente)
    st.markdown("#### Distribuție relativă (procente) pe țări")
    ct_country_category_pct = pd.crosstab(
        df_country_cat["country"], df_country_cat["category"]
    )
    ct_country_category_pct = (
        ct_country_category_pct
        .div(ct_country_category_pct.sum(axis=1), axis=0)
        .reset_index()
    )
    ct_long_pct = ct_country_category_pct.melt(
        id_vars="country", var_name="category", value_name="percent"
    )

    fig_stack_pct = px.bar(
        ct_long_pct,
        x="country",
        y="percent",
        color="category",
        title="Distribuția relativă a categoriilor pe țări",
        labels={"country": "Țară", "percent": "Proporție (%)"},
    )
    fig_stack_pct.update_layout(xaxis_tickangle=-45, yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_stack_pct, use_container_width=True)

    # REGIUNI (province)
    st.markdown("### Regiuni (province)")

    region_stats = dfc.groupby("province", observed=False).agg(
        mean_price=("price", "mean"),
        mean_points=("points", "mean"),
        count=("province", "count"),
    ).reset_index()

    min_wines_region = st.slider(
        "Minim vinuri / regiune pentru diagrame",
        min_value=20,
        max_value=int(region_stats["count"].max()),
        value=30,
        step=5,
    )
    region_stats_f = region_stats[region_stats["count"] >= min_wines_region]

    col1, col2 = st.columns(2)
    with col1:
        fig_r1 = px.bar(
            region_stats_f.sort_values("mean_points", ascending=False),
            x="province",
            y="mean_points",
            title=f"Punctaj mediu pe regiune (>= {min_wines_region} vinuri)",
            labels={"province": "Regiune", "mean_points": "Punctaj mediu"},
        )
        fig_r1.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig_r1, use_container_width=True)
    with col2:
        fig_r2 = px.bar(
            region_stats_f.sort_values("mean_price", ascending=False),
            x="province",
            y="mean_price",
            title=f"Preț mediu pe regiune (>= {min_wines_region} vinuri)",
            labels={"province": "Regiune", "mean_price": "Preț mediu (USD)"},
        )
        fig_r2.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig_r2, use_container_width=True)

    # distrib. categoriilor pe regiuni
    st.markdown("#### Distribuția categoriilor pe regiuni (stacked)")

    df_region_cat = dfc[dfc["province"].isin(region_stats_f["province"])].copy()
    ct_region_category = pd.crosstab(
        df_region_cat["province"], df_region_cat["category"]
    ).reset_index()
    ct_long_reg = ct_region_category.melt(
        id_vars="province", var_name="category", value_name="count"
    )
    fig_reg_stack = px.bar(
        ct_long_reg,
        x="province",
        y="count",
        color="category",
        title="Distribuția vinurilor după categorii și regiuni",
        labels={"province": "Regiune", "count": "Număr vinuri"},
    )
    fig_reg_stack.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig_reg_stack, use_container_width=True)


# ------------------------------------------------------------
# TAB: CATEGORII
# ------------------------------------------------------------

def tab_categories(df: pd.DataFrame):
    st.subheader("Analiza pe categorii de vin")

    dfc = df.copy()
    cat_stats = dfc.groupby("category", observed=False).agg(
        count=("category", "count"),
        mean_points=("points", "mean"),
        mean_price=("price", "mean"),
        mean_quality_price=("quality_price", "mean"),
    ).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(
            cat_stats,
            x="category",
            y="count",
            title="Număr de vinuri pe categorie",
            labels={"category": "Categorie", "count": "Număr vinuri"},
        )
        fig1.update_traces(text=cat_stats["count"], textposition="outside")
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.bar(
            cat_stats,
            x="category",
            y="mean_points",
            title="Punctaj mediu pe categorie",
            labels={"category": "Categorie", "mean_points": "Punctaj mediu"},
        )
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.bar(
            cat_stats,
            x="category",
            y="mean_price",
            title="Preț mediu pe categorie",
            labels={"category": "Categorie", "mean_price": "Preț mediu (USD)"},
        )
        fig3.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        fig4 = px.bar(
            cat_stats,
            x="category",
            y="mean_quality_price",
            title="quality_price mediu pe categorie",
            labels={"category": "Categorie", "mean_quality_price": "quality_price mediu"},
        )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)

    # distribuția punctajelor (similar notebook)
    st.markdown("### Distribuția punctajelor (points)")
    fig_hist_points = px.histogram(
        dfc,
        x="points",
        nbins=25,
        title="Distribuția punctajelor",
        labels={"points": "Punctaj"},
    )
    st.plotly_chart(fig_hist_points, use_container_width=True)


# ------------------------------------------------------------
# TAB: RAPORT PREȚ / CALITATE
# ------------------------------------------------------------

def tab_quality_price(df: pd.DataFrame):
    st.subheader("Raport preț / calitate (quality_price)")

    dfc = df.copy()

    # quality_price vs price, colorat după punctaj
    fig_sc = px.scatter(
        dfc,
        x="price",
        y="quality_price",
        color="points",
        hover_data=["country", "category", "variety", "winery"],
        title="quality_price vs Preț (colorat după punctaj)",
        labels={"price": "Preț (USD)", "quality_price": "Raport preț/calitate"},
        color_continuous_scale="Viridis",
        opacity=0.5,
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # Agregare pe țară (similar cu notebook)
    st.markdown("### quality_price mediu pe țări")

    quality_stats = dfc.groupby("country", observed=False).agg(
        mean_quality_price=("quality_price", "mean"),
        median_quality_price=("quality_price", "median"),
        mean_price=("price", "mean"),
        mean_points=("points", "mean"),
        count=("country", "count"),
    ).reset_index()

    min_wines = st.slider(
        "Minim vinuri / țară pentru analiza quality_price",
        min_value=10,
        max_value=int(quality_stats["count"].max()),
        value=10,
        step=5,
    )
    quality_stats_f = quality_stats[quality_stats["count"] >= min_wines]

    col1, col2 = st.columns(2)
    with col1:
        fig_qp = px.bar(
            quality_stats_f.sort_values("mean_quality_price", ascending=False),
            x="country",
            y="mean_quality_price",
            title=f"quality_price mediu pe țări (>= {min_wines} vinuri)",
            labels={"country": "Țară", "mean_quality_price": "quality_price mediu"},
        )
        fig_qp.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig_qp, use_container_width=True)
    with col2:
        fig_mp = px.bar(
            quality_stats_f.sort_values("mean_price", ascending=False),
            x="country",
            y="mean_price",
            title=f"Preț mediu pe țări (>= {min_wines} vinuri)",
            labels={"country": "Țară", "mean_price": "Preț mediu (USD)"},
        )
        fig_mp.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig_mp, use_container_width=True)

    # scatter: mean_price vs mean_quality_price
    st.markdown("#### Preț mediu vs quality_price mediu pe țări")
    fig_sc2 = px.scatter(
        quality_stats_f,
        x="mean_price",
        y="mean_quality_price",
        size="count",
        color="mean_points",
        hover_name="country",
        title=f"Preț mediu vs quality_price mediu pe țări (>= {min_wines} vinuri)",
        labels={
            "mean_price": "Preț mediu (USD)",
            "mean_quality_price": "quality_price mediu",
        },
        color_continuous_scale="Plasma",
    )
    st.plotly_chart(fig_sc2, use_container_width=True)


# ------------------------------------------------------------
# TAB: ANALIZĂ TEXT (wordcloud + word–metric heatmap)
# ------------------------------------------------------------

def tab_text_analysis(df: pd.DataFrame):
    st.subheader("Analiză text a descrierilor")

    descriptions_clean, tokens_per_row, word_freq, all_tokens = prepare_text_corpus(
        df["description"]
    )

    st.markdown("### Cele mai frecvente cuvinte (fără stopwords)")
    n_top = st.slider("Număr cuvinte de afișat", 10, 50, 30, step=5)
    most_common = word_freq.most_common(n_top)
    mc_df = pd.DataFrame(most_common, columns=["word", "freq"])
    st.dataframe(mc_df)

    st.markdown("### Wordcloud (similar notebook)")
    # generăm wordcloud cu Matplotlib și îl afișăm
    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        max_words=200,
    ).generate(" ".join(all_tokens))

    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig_wc)

    st.markdown("### Analiză corelație cuvinte–metrice (price, points, quality_price)")
    word_metric_summary = compute_word_metric_summary(
        df.copy(), descriptions_clean
    )

    st.dataframe(
        word_metric_summary[
            [
                "word",
                "n_with",
                "frac_with",
                "price_diff",
                "points_diff",
                "quality_price_diff",
            ]
        ].round(3)
    )

    # heatmap diferențe de medii (similar cu notebook, dar cu Seaborn)
    fig_hm, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        word_metric_summary.set_index("word")[
            ["price_diff", "points_diff", "quality_price_diff"]
        ].round(3),
        annot=True,
        cmap="coolwarm",
        center=0,
        ax=ax,
    )
    ax.set_title("Diferență de medii (with - without) pentru cuvinte frecvente")
    st.pyplot(fig_hm)

    st.markdown("### Distribuția lungimii descrierilor (în cuvinte)")
    desc_lengths_words = descriptions_clean.apply(lambda x: len(word_tokenize(x)))
    fig_len, ax_len = plt.subplots(figsize=(8, 4))
    ax_len.hist(
        desc_lengths_words, bins=40, color="steelblue", edgecolor="black", alpha=0.7
    )
    ax_len.set_title("Distribuția lungimii descrierilor (număr de cuvinte)")
    ax_len.set_xlabel("Număr de cuvinte")
    ax_len.set_ylabel("Frecvență")
    st.pyplot(fig_len)


# ------------------------------------------------------------
# TAB: CĂUTARE VINURI DUPĂ DESCRIERE
# ------------------------------------------------------------

def tab_search(df: pd.DataFrame):
    st.subheader("Căutare vinuri după descriere text")

    st.markdown(
        "Introdu o descriere dorită (de ex. *ripe black fruit, soft tannins, fresh acidity*) "
        "și vom căuta cele mai similare vinuri."
    )

    query = st.text_area(
        "Descriere vin dorit",
        value="ripe black fruit, soft tannins, fresh acidity",
        height=100,
    )

    apply_filters_to_search = st.checkbox(
        "Aplică și filtrele globale la căutare (dacă sunt setate în sidebar)",
        value=True,
    )

    df_base = df.copy() if apply_filters_to_search else load_data()

    if st.button("Caută vinuri"):
        if not query.strip():
            st.warning("Te rog introdu o descriere pentru căutare.")
            return

        with st.spinner("Căutare în desfășurare..."):
            results = search_wines(df_base, query, top_n=30)

        if results.empty:
            st.info("Nu au fost găsite rezultate pentru această descriere.")
        else:
            st.success(f"Găsite {len(results)} rezultate (top similare).")
            # afișăm un subset de coloane plus scorul
            columns_to_show = [
                "country", "province", "variety", "category",
                "points", "price", "alcohol", "quality_price",
                "title", "description", "similarity",
            ]
            existing_cols = [c for c in columns_to_show if c in results.columns]
            st.dataframe(
                results[existing_cols].sort_values("similarity", ascending=False)
            )


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="Wine Explorer - Analiză & Căutare",
        layout="wide",
    )

    st.title("Wine Explorer")

    st.markdown(
        """
        """
    )

    df = load_data()
    df_filtered = apply_filters(df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Overview",
            "Țări & Regiuni",
            "Categorii",
            "Raport Preț/Calitate",
            "Analiză Text",
            "Căutare după descriere",
        ]
    )

    with tab1:
        tab_overview(df_filtered)
    with tab2:
        tab_countries_regions(df_filtered)
    with tab3:
        tab_categories(df_filtered)
    with tab4:
        tab_quality_price(df_filtered)
    with tab5:
        tab_text_analysis(df_filtered)
    with tab6:
        tab_search(df_filtered)


if __name__ == "__main__":
    main()
