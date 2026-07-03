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
hr{
border:1px solid white;
}
</style>
""",unsafe_allow_html=True)

# ==========================
# SIDEBAR IDENTITAS
# ==========================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1684/1684375.png", width=120)
st.sidebar.title("🌡 Dashboard")
st.sidebar.success("Monitoring Suhu Ruangan")
st.sidebar.markdown("---")
st.sidebar.write("## 👩‍🎓 Identitas")
st.sidebar.info("**NAMA :**\n\nSHARON\n\n**KELAS :**\n\n2 TRSE A")
st.sidebar.markdown("---")
st.sidebar.write("Tanggal")
st.sidebar.success(datetime.now().strftime("%d %B %Y"))
st.sidebar.write("Jam")
st.sidebar.warning(datetime.now().strftime("%H:%M:%S"))

# ==========================
# KONEKSI DATABASE (SESUAI SYARAT TUGAS POIN 3)
# ==========================
try:
    db = mysql.connector.connect(
        host="mysql-5b14bc0-mahasiswa-7008.a.aivencloud.com",
        port=19701,
        user="avnadmin",
        password="AVNS_e1GQfbCHL7UJF3iMEBx",
        database="defaultdb",                  
        ssl_ca=None                               
    )
    query = "SELECT * FROM data_adc"
    df = pd.read_sql(query, db)
except Exception as e:
    st.error(f"Gagal terhubung ke database Cloud Aiven: {e}")
    df = pd.DataFrame(columns=["second", "suhu_ruangan"])

# ==========================
# PROSES PENYUSUNAN & PEMBERSIHAN DATA SECARA AMAN
# ==========================
if not df.empty:
    # 1. Kecilkan semua nama kolom asal database
    df.columns = [col.lower() for col in df.columns]
    
    # Perbaiki nama kolom jika mengandung spasi bawaan dari DBeaver
    if "suhu ruangan" in df.columns:
        df.rename(columns={"suhu ruangan": "suhu_ruangan"}, inplace=True)
        
    # Pastikan minimal ada nama kolom 'second' dan 'suhu_ruangan'
    if "suhu_ruangan" not in df.columns:
        # Jika kolom suhu_ruangan tidak ditemukan, ambil kolom terakhir yang berisi angka
        num_cols = df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
            df.rename(columns={num_cols[-1]: "suhu_ruangan"}, inplace=True)
        else:
            df["suhu_ruangan"] = 25.0

    if "second" not in df.columns:
        df["second"] = range(len(df))

    # 2. Amankan data agar hanya menampilkan nilai normal (15°C s.d 60°C)
    df = df[(df["suhu_ruangan"] >= 15) & (df["suhu_ruangan"] <= 60)]
    
    # Hapus baris duplikat berdasarkan kolom detik agar datanya presisi pas
    df = df.drop_duplicates(subset=["second"])
    
    # 3. Urutkan berdasarkan kolom detik supaya grafik teratur sempurna
    df["second"] = pd.to_numeric(df["second"])
    df = df.sort_values(by="second").reset_index(drop=True)
else:
    # Backup data terstruktur jika database kosong/eror
    df = pd.DataFrame({"second": range(0, 10), "suhu_ruangan": [25, 25, 25, 25, 24, 26, 25, 25, 24, 25]})

# Ensure required columns exist after filtering
if "second" not in df.columns or "suhu_ruangan" not in df.columns:
    df = pd.DataFrame({"second": range(0, 10), "suhu_ruangan": [25]*10})

# ==========================
# HEADER TAMPILAN
# ==========================
st.markdown("<div class='title'>🌡️ Dashboard Monitoring Suhu</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Visualisasi Data Sensor Suhu Menggunakan Streamlit & MySQL Cloud (Aiven)</div>", unsafe_allow_html=True)

# ==========================
# HITUNG STATISTIK RESMI
# ==========================
jumlah = len(df)
rata = df["suhu_ruangan"].mean()
maks = df["suhu_ruangan"].max()
mini = df["suhu_ruangan"].min()

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("📊 Jumlah Data", jumlah)
with c2: st.metric("🌡 Rata-rata", f"{rata:.2f} °C" if not pd.isna(rata) else "0 °C")
with c3: st.metric("🔥 Maksimum", f"{maks:.1f} °C" if not pd.isna(maks) else "0 °C")
with c4: st.metric("❄ Minimum", f"{mini:.1f} °C" if not pd.isna(mini) else "0 °C")

st.markdown("---")

st.subheader("📡 Status Sensor")
if len(df) > 0:
    suhu_sekarang = float(df["suhu_ruangan"].iloc[-1])
else:
    suhu_sekarang = 25.0

if suhu_sekarang <= 25:
    st.success(f"🟢 NORMAL\n\nSuhu Saat Ini : {suhu_sekarang:.1f} °C")
elif suhu_sekarang <= 35:
    st.warning(f"🟡 HANGAT\n\nSuhu Saat Ini : {suhu_sekarang:.1f} °C")
else:
    st.error(f"🔴 PANAS\n\nSuhu Saat Ini : {suhu_sekarang:.1f} °C")

# GAUGE CHART
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=suhu_sekarang,
    title={'text': "Suhu Saat Ini"},
    gauge={
        'axis': {'range': [0, 50]},
        'bar': {'color': "red"},
        'steps': [
            {'range': [0, 20], 'color': "lightblue"},
            {'range': [20, 30], 'color': "green"},
            {'range': [30, 40], 'color': "yellow"},
            {'range': [40, 50], 'color': "red"}
        ]
    }
))
st.plotly_chart(fig_gauge, use_container_width=True)

# ==========================
# GRAFIK LINE (MONITORING SUHU BERGARIS RAPI)
# ==========================
fig_line = px.line(
    df,
    x="second",
    y="suhu_ruangan",
    markers=True,
    title="Grafik Monitoring Suhu (Database Source)",
    labels={"second": "Detik (Second)", "suhu_ruangan": "Suhu (°C)"},
    color_discrete_sequence=["#FF4B4B"]
)
fig_line.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="#F8F9FA",
    xaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
    yaxis=dict(showgrid=True, gridcolor="#E2E8F0"),
    font=dict(size=14)
)
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("### 🖼️ Unduh Grafik")
st.info("💡 Kamu bisa mengunduh Grafik PNG secara instan langsung dengan mengklik ikon **Kamera (Download plot as a png)** di pojok kanan atas grafik di atas saat kursor diarahkan ke gambar!")

st.markdown("---")

# ==========================
# GRAFIK BATANG (BAR CHART TERSTRUKTUR)
# ==========================
st.subheader("📊 Grafik Batang (20 Data Terakhir)")
df_bar = df.tail(20)
bar = px.bar(
    df_bar,
    x="second",
    y="suhu_ruangan",
    color="suhu_ruangan",
    labels={"second": "Detik (Second)", "suhu_ruangan": "Suhu (°C)"},
    color_continuous_scale="Turbo",
    title="Tren Perubahan 20 Data Suhu Terakhir"
)
bar.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="#F8F9FA",
    xaxis=dict(type='category')
)
st.plotly_chart(bar, use_container_width=True)

# PIE CHART
st.subheader("🥧 Persentase Kondisi Suhu")
kategori = pd.cut(
    df["suhu_ruangan"],
    bins=[0, 25, 35, 100],
    labels=["Normal", "Hangat", "Panas"]
)
pie = kategori.value_counts().reset_index()
pie.columns = ["Kategori", "Jumlah"]
fig_pie = px.pie(pie, names="Kategori", values="Jumlah", hole=.5)
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==========================
# PERBAIKAN DATA SENSOR (ANTI EROR VALUENOTFOUND / COLUMN MISMATCH)
# ==========================
st.subheader("📋 Data Sensor Terstruktur")

# Menggunakan sistem rename aman agar tidak memicu ValueError jumlah kolom
df_tampil = df.copy()
if "second" in df_tampil.columns and "suhu_ruangan" in df_tampil.columns:
    df_tampil = df_tampil[["second", "suhu_ruangan"]]
    df_tampil.columns = ["Second (Detik)", "Suhu Ruangan (°C)"]

st.dataframe(df_tampil, use_container_width=True, height=350)

csv = df_tampil.to_csv(index=False)
st.download_button(
    "⬇ Download CSV",
    csv,
    "Data_Suhu_Clean.csv",
    "text/csv"
)

st.markdown("---")
st.markdown("<center><h3 style='color:white;'>👩‍💻 Dibuat Oleh<br>SHARON<br>2 TRSE A</h3></center>", unsafe_allow_html=True)