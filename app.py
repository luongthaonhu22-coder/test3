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
# CẤU HÌNH TRANG & CSS CAO CẤP (GIỮ NGUYÊN MÀU SẮC - THEO HÌNH 2)
# ==========================================
st.set_page_config(page_title="ELOGS | Workspace", page_icon="⚓", layout="wide")

st.markdown("""
<style>
    /* Đổi màu nền tổng thể thành xám nhạt sang trọng */
    .stApp { background-color: #f4f7f6; }
    
    /* BIẾN ĐỔI THANH TABS NGANG THÀNH THANH ĐIỀU HƯỚNG SANG TRỌNG (HÌNH 2) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 12px; 
        background-color: #0A2647; /* Giữ màu xanh Navy đậm */
        padding: 10px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] { 
        color: #ffffff !important; 
        background-color: transparent; 
        padding: 10px 24px; 
        border-radius: 8px;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    /* Hiệu ứng khi di chuột qua Tab */
    .stTabs [data-baseweb="tab"]:hover { 
        background-color: rgba(255, 255, 255, 0.15) !important; 
    }
    /* Giao diện khi Tab được chọn chủ động */
    .stTabs [aria-selected="true"] { 
        background-color: #185ADB !important; /* Giữ màu xanh Royal */
        color: white !important;
        box-shadow: 0 2px 8px rgba(24, 90, 219, 0.4);
    }
    
    /* Cấu hình các thẻ thông số Thống kê (Metrics Cards) 3D */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e4e8;
        padding: 22px;
        border-radius: 14px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    }
    
    /* Làm đẹp Bảng chỉnh sửa dữ liệu */
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    
    /* Thiết kế nút bấm chuẩn chuyên nghiệp */
    div.stButton > button { 
        background-color: #185ADB !important; 
        color: white !important; 
        border-radius: 8px !important; 
        font-weight: 600 !important; 
        border: none !important; 
        padding: 10px 24px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover { 
        background-color: #0A2647 !important; 
        box-shadow: 0 4px 12px rgba(24, 90, 219, 0.3) !important;
    }
    
    /* Đồng bộ font chữ toàn hệ thống */
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
# TIÊU ĐỀ CHÍNH VÀ THANH ĐIỀU HƯỚNG TABS NGANG (HÌNH 2)
# ==========================================
st.title("⚓ HỆ THỐNG QUẢN LÝ LOGISTICS - ELOGS")
st.markdown("Hệ thống tối ưu hóa quy trình nhắc việc và gửi chứng từ tự động.")

# Khởi tạo các Tab ngang ở phía trên cùng
tab_dashboard, tab_mail, tab_settings = st.tabs(["📊 TỔNG QUAN (DASHBOARD)", "📧 PRE-ALERT & GỬI EMAIL", "⚙️ CÀI ĐẶT HỆ THỐNG"])

# ==========================================
# TAB 1: DASHBOARD (TỔNG QUAN)
# ==========================================
with tab_dashboard:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Hiệu suất Công việc hôm nay")
    
    # Tính toán số liệu đầu vào
    df = st.session_state.tasks_df
    total_tasks = len(df)
    done_tasks = len(df[df["⏳ Trạng thái"] == "Hoàn thành"])
    important_tasks = len(df[df["🚩 Quan trọng"] == True])
    
    # Hiển thị các thẻ Metrics hàng ngang xếp đều nhau
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📦 Tổng số Việc", total_tasks)
    m2.metric("✅ Đã hoàn thành", done_tasks)
    m3.metric("🔥 Cần xử lý gấp", important_tasks, delta_color="inverse")
    m4.metric("📈 Hiệu suất", f"{int((done_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Khu vực bảng tác vụ tương tác điện tử
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
    
    # Khu vực cảnh báo hạn chót và biểu đồ phân tích
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
# TAB 2: API & GỬI EMAIL
# ==========================================
with tab_mail:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Trung tâm Tra cứu Vận đơn (API)")
    
    scanned_data = st.text_input("Nhập mã Booking cần kiểm tra (Ví dụ: BKG-123 hoặc BKG-456):", placeholder="BKG-123")
    
    if st.button("Kích hoạt Tra cứu Hệ thống"):
        if scanned_data:
            with st.spinner('Đang kết nối API và đồng bộ hóa đám mây...'):
                time.sleep(1.2) 
                logistics_data = {
                    "BKG-123": {"Mã BKG": "BKG-123", "Trạng thái": "On Board", "Tàu vận chuyển": "EVER GIVEN", "Cảng hạ": "Cát Lái"},
                    "BKG-456": {"Mã BKG": "BKG-456", "Trạng thái": "Pending", "Tàu vận chuyển": "MAERSK ESSEN", "Cảng hạ": "Hải Phòng"}
                }
                if scanned_data in logistics_data:
                    st.success("🎉 Kết nối thành công! Dữ liệu trả về từ Server:")
                    st.json(logistics_data[scanned_data])
                else:
                    st.error("❌ Không tìm thấy dữ liệu vận đơn này trên hệ thống!")
        else:
            st.warning("⚠️ Vui lòng nhập mã Booking trước khi kiểm tra!")
                
    st.markdown("---")
    
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
# TAB 3: CÀI ĐẶT
# ==========================================
with tab_settings:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚙️ Cấu hình hệ thống nâng cao")
    st.info("Tính năng phân quyền đại lý, kết nối API nhà xe và thiết lập thông số EDI sẽ xuất hiện trong bản cập nhật lớn tiếp theo.")
