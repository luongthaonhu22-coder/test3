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
    
    /* 🎨 BIẾN MENU SIDEBAR THÀNH CÁC KHỐI BO TRÒN HIỆN ĐẠI */
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
        gap: 12px; /* Tạo khoảng cách đều giữa các menu */
    }
    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.06); /* Nền trong suốt mờ */
        padding: 12px 20px;
        border-radius: 16px !important; /* ĐỘ BO TRÒN CAO */
        border: 1px solid rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    /* Hiệu ứng khi di chuột vào Menu */
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15); /* Sáng lên */
        transform: translateX(6px); /* Trượt nhẹ sang phải cho có cảm giác tương tác */
        border-color: rgba(255,255,255,0.3);
    }
    /* Ẩn cái dấu chấm tròn mặc định của Streamlit đi cho đẹp */
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
        border-radius: 16px; /* Bo tròn đồng bộ */
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
        border-radius: 20px !important; /* Nút bấm dạng viên thuốc */
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
    
    /* Đồng bộ font chữ */
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
# THANH ĐIỀU HƯỚNG BÊN TRÁI (SIDEBAR) ĐÃ BO TRÒN
# ==========================================
st.sidebar.markdown("## ⚓ ELOGS Workspace")
st.sidebar.markdown("---")
# Menu nay đã được CSS biến hóa thành các nút bấm bo tròn
menu = st.sidebar.radio("CHỨC NĂNG CHÍNH:", [
    "📊 Tổng quan (Dashboard)", 
    "📡 Tra cứu & Gửi Email", 
    "⚙️ Cài đặt hệ thống"
])
st.sidebar.markdown("---")
st.sidebar.info("💡 **Giao diện 2.0:** Thiết kế bo tròn giúp giảm mỏi mắt và tăng khả năng tập trung vào dữ liệu.")

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
    with colB:
        st.subheader("📊 Tỷ lệ tiến độ công việc")
        status_counts = edited_df["⏳ Trạng thái"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 2.3))
        fig.patch.set_facecolor('#f4f7f6')
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=['#4CAF50','#FFC107','#F44336'])
        ax.set_ylabel("") 
        st.pyplot(fig)

# ==========================================
# MÀN HÌNH 2: API & GỬI EMAIL
# ==========================================
elif menu == "📡 Tra cứu & Gửi Email":
    st.title("Trung tâm Xử lý Dữ liệu Ngoại vi")
    
    with st.container():
        st.subheader("🔍 Kết nối API: Tra cứu vận đơn")
        scanned_data = st.text_input("Nhập mã Booking cần kiểm tra (Ví dụ: BKG-123):", placeholder="BKG-123")
        
        if st.button("Kích hoạt Tra cứu Hệ thống"):
            if scanned_data:
                with st.spinner('Đang kết nối API và đồng bộ hóa đám mây...'):
                    time.sleep(1.2) 
                    logistics_data = {
                        "BKG-123": {"Mã BKG": "BKG-123", "Trạng thái": "On Board", "Tàu vận chuyển": "EVER GIVEN", "Cảng hạ": "Cát Lái"},
                        "BKG-456": {"Mã BKG": "BKG-456", "Trạng thái": "Pending", "Tàu vận chuyển": "MAERSK ESSEN", "Cảng hạ": "Hải Phòng"}
                    }
                    if scanned_data in logistics_data:
                        st.success("🎉 Truy xuất thành công!")
                        st.json(logistics_data[scanned_data])
                    else:
                        st.error("❌ Không tìm thấy dữ liệu vận đơn này trên hệ thống!")
            else:
                st.warning("⚠️ Vui lòng nhập mã Booking trước khi kiểm tra!")
                
    st.markdown("---")
    
    with st.container():
        st.subheader("📧 Thiết lập gửi Email Pre-Alert")
        col1, col2 = st.columns(2)
        with col1: receiver_email = st.text_input("Gửi đến đối tác (To):")
        with col2: cc_email = st.text_input("Đồng gửi nội bộ (CC):")
            
        col_a, col_b, col_c = st.columns(3)
        booking_no = col_a.text_input("Mã số Booking:", "BKG-VNM-998877")
        container_no = col_b.text_input("Ký hiệu Container:", "CMAU1234567")
        cut_off = col_c.text_input("Thời gian Cut-off:", "17:00 - 25/06/2026")
        
        uploaded_file = st.file_uploader("Đính kèm tệp chứng từ (Hình ảnh, PDF):")
        
        if st.button("🚀 PHÁT HÀNH EMAIL THÔNG BÁO"):
            if not receiver_email:
                st.error("⚠️ Bạn chưa điền địa chỉ Email người nhận!")
            else:
                with st.spinner('Đang đóng gói chứng từ và gửi SMTP...'):
                    try:
                        file_name = f"Booking_Note_{booking_no}.html"
                        file_content = f"<html><body><h2>ELOGS LOGISTICS SYSTEM</h2><hr><ul><li><b>Booking:</b> {booking_no}</li><li><b>Container:</b> {container_no}</li><li><b>Cut-off:</b> <span style='color:red;'>{cut_off}</span></li></ul></body></html>"
                        with open(file_name, "w", encoding="utf-8") as f: f.write(file_content)

                        msg = MIMEMultipart()
                        msg['From'], msg['To'], msg['Subject'] = SENDER_EMAIL, receiver_email, f"[URGENT] Lịch Cut-off lô hàng {booking_no}"
                        if cc_email: msg['Cc'] = cc_email
                        msg.attach(MIMEText("Kính gửi quý đối tác, vui lòng kiểm tra thông tin lịch trình chi tiết trong tệp đính kèm.", 'plain', 'utf-8'))

                        with open(file_name, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename= {file_name}")
                        msg.attach(part)

                        if uploaded_file:
                            file_part = MIMEBase("application", "octet-stream")
                            file_part.set_payload(uploaded_file.read())
                            encoders.encode_base64(file_part)
                            file_part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                            msg.attach(file_part)

                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(SENDER_EMAIL, APP_PASSWORD)
                        server.send_message(msg)
                        server.quit()
                        st.success("🎉 Hệ thống đã gửi email thông báo thành công đến đối tác!")
                    except Exception as e:
                        st.error(f"❌ Gặp sự cố khi gửi thư qua Gmail: {e}")

# ==========================================
# MÀN HÌNH 3: CÀI ĐẶT
# ==========================================
elif menu == "⚙️ Cài đặt hệ thống":
    st.title("⚙️ Cài đặt Hệ thống")
    st.info("Tính năng phân quyền đại lý, kết nối API nhà xe và thiết lập thông số EDI sẽ xuất hiện trong bản cập nhật lớn tiếp theo.")
