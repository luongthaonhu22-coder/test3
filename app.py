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
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=['#ff9999','#66b3ff','#99ff99'])
        ax.set_ylabel("") 
        st.pyplot(fig)
        
    with col_chart2:
        st.write("Số lượng đầu việc theo nhãn:")
        label_counts = edited_df["🏷️ Nhãn"].value_counts()
        st.bar_chart(label_counts)

# ==========================================
# TAB 2: PRE-ALERT & CHỨNG TỪ (KẾT NỐI MOCK API SERVER)
# ==========================================
with tab_mail:
    st.subheader("📡 Tra cứu lô hàng từ Hệ thống API")
    scanned_data = st.text_input("Nhập mã Booking cần tra cứu (Ví dụ: BKG-123 hoặc BKG-456):", placeholder="BKG-123")
    
    # NÚT BẤM GỌI ĐẾN MOCK SERVER CỦA BẠN
    if st.button("🔍 Tra cứu thông tin từ Server API"):
        if scanned_data:
            with st.spinner('Đang kết nối tới Server cổng 8000...'):
                try:
                    response = requests.get(f"http://127.0.0.1:8000/shipment/{scanned_data}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.warning(f"⚠️ Hệ thống báo: {data['error']}")
                        else:
                            st.success(f"🎉 Kết nối thành công! Dữ liệu trả về từ Server: {data}")
                    else:
                        st.error(f"❌ Server phản hồi lỗi mã: {response.status_code}")
                except Exception as e:
                    st.error("🔌 Không thể kết nối tới Server API! Bạn đã chạy file 'mock_server.py' ở PowerShell chưa?")
        else:
            st.warning("⚠️ Vui lòng nhập mã Booking trước khi tra cứu!")
        
    st.markdown("---")
    st.subheader("📎 Gửi thông báo kèm chứng từ Email")
    
    colA, colB = st.columns(2)
    with colA: receiver_email = st.text_input("Gửi đến (To - Bắt buộc):")
    with colB: cc_email = st.text_input("Đồng gửi (CC - Tùy chọn):")
        
    col1, col2, col3 = st.columns(3)
    booking_no = col1.text_input("Số Booking:", "BKG-VNM-998877")
    container_no = col2.text_input("Số Container:", "CMAU1234567")
    cut_off = col3.text_input("Cut-off:", "17:00 - 25/06/2026")
    
    uploaded_file = st.file_uploader("Tải ảnh chứng từ lên (JPG, PNG, PDF - Tùy chọn):", type=['jpg', 'jpeg', 'png', 'pdf'])
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 XÁC NHẬN GỬI THÔNG BÁO EMAIL"):
        if not receiver_email:
            st.error("⚠️ Vui lòng điền Email người nhận!")
        else:
            with st.spinner('Hệ thống đang gửi email...'):
                try:
                    file_name = f"Booking_Note_{booking_no}.html"
                    file_content = f"""<html><body><h2>CÔNG TY LOGISTICS ELOGS</h2><hr><ul><li><b>Booking:</b> {booking_no}</li><li><b>Container:</b> {container_no}</li><li><b>Cut-off:</b> <span style='color:red;'>{cut_off}</span></li></ul></body></html>"""
                    with open(file_name, "w", encoding="utf-8") as f: f.write(file_content)

                    msg = MIMEMultipart()
                    msg['From'], msg['To'] = SENDER_EMAIL, receiver_email
                    if cc_email: msg['Cc'] = cc_email
                    msg['Subject'] = f"[URGENT] Thông báo lịch Cut-off lô hàng {booking_no}"
                    msg.attach(MIMEText("Chi tiết lô hàng vui lòng kiểm tra file đính kèm.", 'plain', 'utf-8'))

                    with open(file_name, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {file_name}")
                    msg.attach(part)

                    if uploaded_file is not None:
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
                    st.success("🎉 Email thông báo đã gửi thành công!")
                except Exception as e:
                    st.error(f"❌ Lỗi gửi mail: {e}")
                    if st.button("🔍 Tra cứu thông tin từ Server API"):
                    if scanned_data:
            with st.spinner('Đang tìm kiếm dữ liệu trên Đám mây...'):
                time.sleep(1.5) # Giả lập thời gian chờ mạng lag
                
                # Kho dữ liệu mô phỏng (Mang từ mock_server sang đây)
                logistics_data = {
                    "BKG-123": {"booking": "BKG-123", "status": "On Board", "vessel": "EVER GIVEN", "port": "Cát Lái"},
                    "BKG-456": {"booking": "BKG-456", "status": "Pending", "vessel": "MAERSK ESSEN", "port": "Hải Phòng"}
                }
                
                if scanned_data in logistics_data:
                    data = logistics_data[scanned_data]
                    st.success(f"🎉 Kết nối thành công! Dữ liệu: {data}")
                else:
                    st.warning("⚠️ Hệ thống báo: Không tìm thấy lô hàng này!")
        else:
            st.warning("⚠️ Vui lòng nhập mã Booking trước khi tra cứu!")
