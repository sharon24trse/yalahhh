import io
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================
# KONFIGURASI HALAMAN
# ==========================
st.set_page_config(
    page_title="Dashboard Monitoring Suhu",
    page_icon="🌡️",
    layout="wide"
)

# ==========================
# CSS CUSTOM
# ==========================
st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#667eea,#764ba2);
}

/* HEADER */
.title{
font-size:42px;
font-weight:bold;
color:white;
text-align:center;
}

.subtitle{
font-size:18px;
color:white;
text-align:center;
margin-top:-15px;
margin-bottom:25px;
}

/* CARD */
.card{
background:white;
padding:20px;
border-radius:20px;
box-shadow:0px 8px 20px rgba(0,0,0,.25);
text-align:center;
transition:0.3s;
}

.card:hover{
transform:scale(1.03);
}

/* FOOTER */
.footer{
text-align:center;
color:white;
font-size:20px;
margin-top:40px;
font-weight:bold;
}

hr{
border:1px solid white;
}

</style>
""",unsafe_allow_html=True)

# ==========================
# SIDEBAR
# ==========================

st.sidebar.image(
"https://cdn-icons-png.flaticon.com/512/1684/1684375.png",
width=120
)

st.sidebar.title("🌡 Dashboard")

st.sidebar.success("Monitoring Suhu Ruangan")

st.sidebar.markdown("---")

st.sidebar.write("## 👩‍🎓 Identitas")

st.sidebar.info("""
**NAMA :**

SHARON

**KELAS :**

2 TRSE A
""")

st.sidebar.markdown("---")

st.sidebar.write("Tanggal")

st.sidebar.success(datetime.now().strftime("%d %B %Y"))

st.sidebar.write("Jam")

st.sidebar.warning(datetime.now().strftime("%H:%M:%S"))

# ==========================
# KONEKSI DATABASE
# ==========================

db = mysql.connector.connect(
    host="mysql-5b14bc0-mahasiswa-7008.a.aivencloud.com",
    port=19701,
    user="avnadmin",
    password="AVNS_e1GQfbCHL7UJF3iMEBx",  # Masukkan password asli dari Aiven
    database="defaultdb",                     # Atau ganti nama database yang kamu buat di Aiven
    ssl_ca=None                               # Tambahkan ini jika Aiven meminta SSL wajib
)


query="SELECT * FROM data_adc"

df=pd.read_sql(query,db)

# ==========================
# HEADER
# ==========================

st.markdown(
"""
<div class='title'>
🌡️ Dashboard Monitoring Suhu
</div>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<div class='subtitle'>
Visualisasi Data Sensor Suhu Menggunakan Streamlit & MySQL
</div>
""",
unsafe_allow_html=True
)
# ==========================
# HITUNG STATISTIK
# ==========================

jumlah=len(df)

rata=df["suhu_ruangan"].mean()

maks=df["suhu_ruangan"].max()

mini=df["suhu_ruangan"].min()
c1,c2,c3,c4=st.columns(4)

with c1:

    st.metric(
    "📊 Jumlah Data",
    jumlah
    )

with c2:

    st.metric(
    "🌡 Rata-rata",
    f"{rata:.2f} °C"
    )

with c3:

    st.metric(
    "🔥 Maksimum",
    f"{maks:.1f} °C"
    )

with c4:

    st.metric(
    "❄ Minimum",
    f"{mini:.1f} °C"
    )
st.markdown("---")

st.subheader("📡 Status Sensor")

suhu_sekarang = df["suhu_ruangan"].iloc[-1]

if suhu_sekarang <= 25:
    st.success(f"🟢 NORMAL\n\nSuhu Saat Ini : {suhu_sekarang} °C")

elif suhu_sekarang <=35:
    st.warning(f"🟡 HANGAT\n\nSuhu Saat Ini : {suhu_sekarang} °C")

else:
    st.error(f"🔴 PANAS\n\nSuhu Saat Ini : {suhu_sekarang} °C")
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=suhu_sekarang,

    title={'text':"Suhu Saat Ini"},

    gauge={
        'axis':{'range':[0,50]},

        'bar':{'color':"red"},

        'steps':[

            {'range':[0,20],'color':"lightblue"},

            {'range':[20,30],'color':"green"},

            {'range':[30,40],'color':"yellow"},

            {'range':[40,50],'color':"red"}

        ]
    }
))

st.plotly_chart(fig,use_container_width=True)


fig = px.line(
    df,
    x="second",
    y="suhu_ruangan",
    markers=True,
    title="Grafik Monitoring Suhu",
    color_discrete_sequence=["red"]
)

fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(size=16)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================
# DOWNLOAD GRAFIK PNG
# ==========================

buffer = io.BytesIO()

fig.write_image(buffer, format="png")

st.download_button(
    label="🖼 Download Grafik PNG",
    data=buffer.getvalue(),
    file_name="Grafik_Monitoring_Suhu.png",
    mime="image/png"
)
st.subheader("📊 Grafik Batang")

bar = px.bar(

    df.tail(20),

    x="second",

    y="suhu_ruangan",

    color="suhu_ruangan",

    color_continuous_scale="Turbo"

)

st.plotly_chart(bar,use_container_width=True)
st.subheader("🥧 Persentase Kondisi Suhu")

kategori = pd.cut(

    df["suhu_ruangan"],

    bins=[0,25,35,50],

    labels=["Normal","Hangat","Panas"]

)

pie = kategori.value_counts().reset_index()

pie.columns=["Kategori","Jumlah"]

fig = px.pie(

    pie,

    names="Kategori",

    values="Jumlah",

    hole=.5

)

st.plotly_chart(fig,use_container_width=True)
st.markdown("---")

st.subheader("📋 Data Sensor")

st.dataframe(

    df,

    use_container_width=True,

    height=350
)
csv = df.to_csv(index=False)

st.download_button(

    "⬇ Download CSV",

    csv,

    "Data_Suhu.csv",

    "text/csv"

)
st.markdown("---")

st.markdown("""

<center>

<h3 style='color:white;'>

👩‍💻 Dibuat Oleh

<br>

SHARON

<br>

2 TRSE A

</h3>

</center>

""",unsafe_allow_html=True)