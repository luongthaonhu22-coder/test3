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
import time # Thư viện dùng để giả lập độ trễ của mạng

# --- HÀM TỰ ĐỘNG HÓA (MÔ PHỎNG BACKEND LOGIC LÊN AWS) ---
def auto_assign_task(task_name, priority_level):
    aws_api_url = "https://ab12cd34ef.execute-api.ap-southeast-1.amazonaws.com/prod/tao-cong-viec"
    payload = {"task_name": task_name, "priority": priority_level}
    try:
        response = requests.post(aws_api_url, json=payload)
        if response.status_code == 200:
            new_task_from_aws = response.json()
            st.session_state.tasks_df = pd.concat(
                [st.session_state.tasks_df, pd.DataFrame([new_task_from_aws])], ignore_index=True
            )
            return True
        return False
    except:
        return False

# --- CẤU HÌNH TÀI KHOẢN EMAIL ---
SENDER_EMAIL = "luongthaonhu22@gmail.com" 
APP_PASSWORD = "yjny odng vbgd czck"     

st.set_page_config(page_title="ELOGS Quản Trị", page_icon="🚢", layout="wide")

# --- MÃ CSS GIAO DIỆN HIỆN ĐẠI SAAS ---
st.markdown("""
<style>
    .stApp { background-color: #EBF0F5 !important; }
    .stDataFrame { border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; background-color: #f1f3f6; padding: 10px 20px; }
    input, textarea, div[data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid #d1d9e6 !important; }
    div.stButton > button { background-color: #185ADB !important; color: white !important; border-radius: 8px !important; font-weight: bold !important; border: none !important; }
    div.stButton > button:hover { background-color: #0A2647 !important; }
    h1, h2, h3 { color: #0F2C59 !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU BẢNG ---
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame({
        "🚩 Quan trọng": [True, False],
        "📌 Tên công việc": ["Khai E-port lô BKG-123", "Gửi SI hãng tàu Evergreen"],
        "🏷️ Nhãn": ["Hàng Nhập", "Chứng Từ"],
        "⏳ Trạng thái": ["Đang làm", "Chưa làm"],
        "📅 Deadline": [date(2026, 6, 30), date(2026, 6, 30)], 
        "💬 Trao đổi / Ghi chú": ["Sếp dặn check kỹ số container", ""]
    })

st.title("🚢 HỆ THỐNG QUẢN LÝ LOGISTICS - ELOGS")

tab_dashboard, tab_mail = st.tabs(["📊 QUẢN TRỊ CÔNG VIỆC (DASHBOARD)", "📧 PRE-ALERT & CHỨNG TỪ"])

# ==========================================
# TAB 1: DASHBOARD QUẢN TRỊ CÔNG VIỆC
# ==========================================
with tab_dashboard:
    st.subheader("Bảng Kế hoạch & Theo dõi tiến độ")
    
    if st.button("🤖 Kích hoạt tạo Task tự động (Mô phỏng hệ thống AWS)"):
        auto_assign_task("Kiểm tra hàng tồn kho mới nhập", "High")
        st.success("Hệ thống đã tự động thêm task mới!")
        st.rerun()
    
    df = st.session_state.tasks_df
    total_tasks = len(df)
    done_tasks = len(df[df["⏳ Trạng thái"] == "Hoàn thành"])
    important_tasks = len(df[df["🚩 Quan trọng"] == True])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng công việc", total_tasks)
    m2.metric("Đã hoàn thành", done_tasks)
    m3.metric("Cần chú ý (Quan trọng)", important_tasks, delta_color="inverse")
    m4.metric("Hiệu suất", f"{int((done_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")
    
    st.markdown("---")

    edited_df = st.data_editor(
        st.session_state.tasks_df,
        key="task_table_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "🚩 Quan trọng": st.column_config.CheckboxColumn("Quan trọng", default=False),
            "🏷️ Nhãn": st.column_config.SelectboxColumn("Nhãn", options=["Hàng Nhập", "Hàng Xuất", "Chứng Từ", "Hiện Trường", "Hải Quan"]),
            "⏳ Trạng thái": st.column_config.SelectboxColumn("Trạng thái", options=["Chưa làm", "Đang làm", "Hoàn thành"]),
            "📅 Deadline": st.column_config.DateColumn("Deadline"),
        }
    )
    st.session_state.tasks_df = edited_df

    st.markdown("### 🔔 Nhắc nhở hệ thống")
    today = date.today()
    for index, row in edited_df.iterrows():
        deadline = row["📅 Deadline"]
        if isinstance(deadline, str): 
            deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
        
        if row["⏳ Trạng thái"] != "Hoàn thành" and deadline < today:
            st.error(f"❌ QUÁ HẠN: **{row['📌 Tên công việc']}** (Deadline: {deadline})")
        elif row["🚩 Quan trọng"] == True and row["⏳ Trạng thái"] != "Hoàn thành":
            st.warning(f"⚠️ Nhiệm vụ quan trọng: **{row['📌 Tên công việc']}** (Hạn: {deadline})") 

    st.markdown("---")
    st.subheader("📊 Báo cáo Kho vận trực quan")
    status_counts = edited_df["⏳ Trạng thái"].value_counts()
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("Tỷ lệ trạng thái công việc:")
        fig, ax = plt.subplots(figsize=(5, 3))
