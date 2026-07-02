import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from datetime import date, datetime
import matplotlib.pyplot as plt
import requests 
import time 

# ==========================================
# CẤU HÌNH TRANG & CSS BO TRÒN (SIDEBAR STYLE)
# ==========================================
st.set_page_config(page_title="ELOGS | Workspace", page_icon="⚓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Đổi màu nền tổng thể thành xám nhạt sang trọng */
    .stApp { background-color: #f4f7f6; }
    
    /* MÀU SẮC CHO THANH SIDEBAR */
    [data-testid="stSidebar"] { 
        background-color: #0A2647; 
    }
    [data-testid="stSidebar"] * { 
        color: #ffffff !important; 
    }
    
    /* BIẾN MENU SIDEBAR THÀNH CÁC KHỐI BO TRÒN HIỆN ĐẠI */
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        gap: 12px;
    }
    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.06); 
        padding: 12px 20px;
        border-radius: 16px !important; 
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    /* Hiệu ứng khi di chuột vào Menu */
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15); 
        transform: translateX(6px); 
        border-color: rgba(255,255,255,0.3);
    }
    /* Ẩn cái dấu chấm tròn mặc định của Streamlit */
    [data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] > div:first-child {
        display: none; 
    }
    [data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] {
        width: 100%;
    }
    
    /* Bo tròn các thẻ thông số Thống kê (Metrics Cards) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e4e8;
        padding: 22px;
        border-radius: 16px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    /* Làm đẹp và bo tròn Bảng dữ liệu */
    .stDataFrame { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    
    /* Bo tròn Nút bấm (Buttons) */
    div.stButton > button { 
        background-color: #185ADB !important; 
        color: white !important; 
        border-radius: 20px !important; 
        font-weight: 600 !important; 
        border: none !important; 
        padding: 10px 24px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { 
        background-color: #0A2647 !important; 
        box-shadow: 0 4px 12px rgba(24, 90, 219, 0.3) !important;
        transform: translateY(-2px);
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    h1, h2, h3 { color: #0A2647 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO KHO DỮ LIỆU TÁC VỤ ---
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame({
        "🚩 Quan trọng": [True, False],
        "📌 Tên công việc": ["Khai E-port lô BKG-123", "Gửi SI hãng tàu Evergreen"],
        "🏷️ Nhãn": ["Hàng Nhập", "Chứng Từ"],
        "⏳ Trạng thái": ["Đang làm", "Chưa làm"],
        "📅 Deadline": [date(2026, 6, 30), date(2026, 6, 30)], 
        "💬 Ghi chú": ["Sếp dặn check kỹ số container", ""]
    })

# --- CẤU HÌNH TÀI KHOẢN EMAIL ---
SENDER_EMAIL = "luongthaonhu22@gmail.com" 
APP_PASSWORD = "yjny odng vbgd czck"     

# ==========================================
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR)
# ==========================================
st.sidebar.markdown("## ⚓ ELOGS Workspace")
st.sidebar.markdown("---")
menu = st.sidebar.radio("CHỨC NĂNG CHÍNH:", [
    "📊 Tổng quan (Dashboard)", 
    "📡 Tra cứu & Gửi Email", 
    "⚙️ Cài đặt hệ thống"
])
st.sidebar.markdown("---")
st.sidebar.info("💡 **Giao diện 3.0:** Đã nâng cấp màn hình kết quả tra cứu API từ dạng JSON thô sang dạng thẻ điều khiển (Visual Tracking Cards) cao cấp.")

# ==========================================
# MÀN HÌNH 1: DASHBOARD
# ==========================================
if menu == "📊 Tổng quan (Dashboard)":
    st.title("Hiệu suất Công việc hôm nay")
    st.markdown("Theo dõi và cập nhật tiến độ các lô hàng theo thời gian thực.")
    
    df = st.session_state.tasks_df
    total_tasks = len(df)
    done_tasks = len(df[df["⏳ Trạng thái"] == "Hoàn thành"])
    important_tasks = len(df[df["🚩 Quan trọng"] == True])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📦 Tổng số Việc", total_tasks)
    m2.metric("✅ Đã hoàn thành", done_tasks)
    m3.metric("🔥 Cần xử lý gấp", important_tasks, delta_color="inverse")
    m4.metric("📈 Hiệu suất", f"{int((done_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("📋 Danh sách tác vụ đang quản lý")
    edited_df = st.data_editor(
        st.session_state.tasks_df,
        key="task_table_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "🚩 Quan trọng": st.column_config.CheckboxColumn("Quan trọng", default=False),
            "🏷️ Nhãn": st.column_config.SelectboxColumn("Nhãn options", options=["Hàng Nhập", "Hàng Xuất", "Chứng Từ", "Hiện Trường", "Hải Quan"]),
            "⏳ Trạng thái": st.column_config.SelectboxColumn("Trạng thái options", options=["Chưa làm", "Đang làm", "Hoàn thành"]),
            "📅 Deadline": st.column_config.DateColumn("Deadline"),
        }
    )
    st.session_state.tasks_df = edited_df

    st.markdown("---")
    
    colA, colB = st.columns([1, 2])
    with colA:
        st.subheader("🔔 Cảnh báo hệ thống")
        today = date.today()
        for index, row in edited_df.iterrows():
            deadline = row["📅 Deadline"]
            if isinstance(deadline, str): deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
            if row["⏳ Trạng thái"] != "Hoàn thành" and deadline < today:
                st.error(f"❌ QUÁ HẠN: {row['📌 Tên công việc']}")
            elif row["🚩 Quan trọng"] == True and row["⏳ Trạng thái"] != "Hoàn thành":
                st.warning(f"⚠️ HẠN GẤP: {row['📌 Tên công việc']}")
