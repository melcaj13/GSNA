import streamlit as st
import pandas as pd
import numpy as np
from textblob import TextBlob
import plotly.express as px
import random

# -----------------------------
# SAYFA AYARLARI
# -----------------------------
st.set_page_config(
    page_title="Hibrit Dijital İtibar Risk Modeli",
    layout="wide",
    page_icon="📊"
)

# -----------------------------
# STİL (MODERN UI)
# -----------------------------
st.markdown("""
<style>
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
}
.big-font {
    font-size: 28px;
    font-weight: bold;
}
.small-font {
    font-size: 14px;
    color: #9CA3AF;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DUMMY VERİ ÜRETİMİ
# -----------------------------
@st.cache_data
def generate_dummy_data(n=100):
    comments = [
        "This place is amazing!",
        "Terrible service, never again.",
        "Food was okay, nothing special.",
        "Absolutely loved it!",
        "Very bad experience.",
        "Not worth the money.",
        "Best restaurant ever!",
        "I will not come back.",
        "Great atmosphere and food.",
        "Worst place I've been."
    ]
    
    data = {
        "Kullanıcı_ID": [f"user_{i}" for i in range(n)],
        "Yorum_Metni": [random.choice(comments) for _ in range(n)],
        "Arkadaş_Sayısı": np.random.randint(1, 500, n)
    }
    
    return pd.DataFrame(data)

# -----------------------------
# NLP ANALİZ
# -----------------------------
def analyze_sentiment(text):
    try:
        return TextBlob(text).sentiment.polarity
    except:
        return 0

# -----------------------------
# VERİ İŞLEME
# -----------------------------
def process_data(df):
    df = df.copy()
    
    # NLP
    df["Polarity"] = df["Yorum_Metni"].apply(analyze_sentiment)
    
    # Negatifleri al
    df["Duygu_Şiddeti"] = abs(df["Polarity"])
    
    # SNA Proxy (normalize edilmiş arkadaş sayısı)
    df["Merkezilik"] = (df["Arkadaş_Sayısı"] - df["Arkadaş_Sayısı"].min()) / (
        df["Arkadaş_Sayısı"].max() - df["Arkadaş_Sayısı"].min()
    )
    
    # Risk skoru
    df["Risk_Skoru"] = df["Duygu_Şiddeti"] * df["Merkezilik"]
    
    return df

# -----------------------------
# SIDEBAR - DOSYA YÜKLEME
# -----------------------------
st.sidebar.title("📂 Veri Yükleme")

uploaded_file = st.sidebar.file_uploader(
    "CSV veya Excel dosyanızı yükleyin",
    type=["csv", "xlsx"]
)

# -----------------------------
# VERİ SEÇİMİ
# -----------------------------
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = generate_dummy_data()

# -----------------------------
# ANALİZ
# -----------------------------
df = process_data(df)

# -----------------------------
# KPI'LAR
# -----------------------------
toplam_yorum = len(df)
ortalama_duygu = df["Polarity"].mean()
yuksek_risk = len(df[df["Risk_Skoru"] > df["Risk_Skoru"].quantile(0.75)])

# -----------------------------
# BAŞLIK
# -----------------------------
st.title("📊 Hibrit Dijital İtibar Risk Dashboard")
st.markdown("e-WOM + NLP + SNA tabanlı risk analizi")

# -----------------------------
# KPI KARTLARI
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-font">Toplam Yorum</div>
        <div class="big-font">{toplam_yorum}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-font">Ortalama Duygu Skoru</div>
        <div class="big-font">{ortalama_duygu:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-font">Yüksek Riskli Müşteri</div>
        <div class="big-font">{yuksek_risk}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# RİSK MATRİSİ
# -----------------------------
st.markdown("## 📈 Risk Matrisi")

fig = px.scatter(
    df,
    x="Merkezilik",
    y="Duygu_Şiddeti",
    size="Risk_Skoru",
    color="Risk_Skoru",
    color_continuous_scale="Reds",
    hover_data=["Kullanıcı_ID"]
)

# Kritik alan (arka plan vurgusu)
fig.add_shape(
    type="rect",
    x0=0.6, y0=0.6,
    x1=1, y1=1,
    fillcolor="red",
    opacity=0.1,
    line_width=0
)

fig.add_annotation(
    x=0.8, y=0.9,
    text="Kritik Risk Bölgesi",
    showarrow=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# TABLO
# -----------------------------
st.markdown("## 🚨 Acil Müdahale Gerektirenler")

top_risk = df.sort_values(by="Risk_Skoru", ascending=False).head(10)

st.dataframe(
    top_risk[["Kullanıcı_ID", "Yorum_Metni", "Risk_Skoru"]],
    use_container_width=True
)
