import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from datetime import date, datetime # <--- Đã bổ sung datetime
import matplotlib.pyplot as plt
import requests 

# --- HÀM TỰ ĐỘNG HÓA (MÔ PHỎNG BACKEND LOGIC) ---
def auto_assign_task(task_name, priority_level):
    """
    Hàm gọi API thực tế lên máy chủ AWS.
    """
    aws_api_url = "https://ab12cd34ef.execute-api.ap-southeast-1.amazonaws.com/prod/tao-cong-viec"
    payload = {
        "task_name": task_name,
        "priority": priority_level
    }
    try:
        response = requests.post(aws_api_url, json=payload)
        if response.status_code == 200:
            new_task_from_aws = response.json()
            st.session_state.tasks_df = pd.concat(
                [st.session_state.tasks_df, pd.DataFrame([new_task_from_aws])], 
                ignore_index=True
            )
            return True
        else:
            st.error(f"Lỗi từ máy chủ AWS: {response.text}")
            return False
    except Exception as e:
        st.error(f"Không thể kết nối mạng tới AWS. Chi tiết lỗi: {e}")
        return False

# --- CẤU HÌNH ---
SENDER_EMAIL = "luongthaonhu22@gmail.com" 
APP_PASSWORD = "yjny odng vbgd czck"     

st.set_page_config(page_title="ELOGS Quản Trị", page_icon="🚢", layout="wide")

# --- NHÚNG MÃ CSS NÂNG CẤP (PHONG CÁCH SaaS HIỆN ĐẠI) ---
st.markdown("""
<style>
    .stApp { background-color: #EBF0F5 !important;
    }
   div.stButton > button {
        background-color: #185ADB !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #0A2647 !important;
    }
</style>
""", unsafe_allow_html=True)


    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        background-color: #f1f3f6;
        padding: 10px 20px;
    }
    
    input, textarea, div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid #d1d9e6 !important;
    }
    
    div.stButton > button {
        background-color: #2563eb !important; 
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    div.stButton > button:hover {
        background-color: #0A2647 !important;
    }
    
    h1, h2, h3 {
        color: #0F2C59 !important;
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO BỘ NHỚ DATA (BẢNG CÔNG VIỆC) ---
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame({
        "🚩 Quan trọng": [True, False],
        "📌 Tên công việc": ["Khai E-port lô BKG-123", "Gửi SI hãng tàu Evergreen"],
        "🏷️ Nhãn": ["Hàng Nhập", "Chứng Từ"],
        "⏳ Trạng thái": ["Đang làm", "Chưa làm"],
        # Sửa từ chuỗi thành kiểu date chuẩn của Python:
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
    
    if st.button("🤖 Kích hoạt tạo Task tự động (Mô phỏng hệ thống)"):
        auto_assign_task("Kiểm tra hàng tồn kho mới nhập", "High")
        st.success("Hệ thống đã tự động thêm task mới!")
        st.rerun()
    
    # 1. BÁO CÁO NHANH (METRICS)
    df = st.session_state.tasks_df
    total_tasks = len(df)
    done_tasks = len(df[df["⏳ Trạng thái"] == "Hoàn thành"])
    important_tasks = len(df[df["🚩 Quan trọng"] == True])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tổng công việc", total_tasks)
    m2.metric("Đã hoàn thành", done_tasks)
    m3.metric("Cần chú ý (Quan trọng)", important_tasks, delta_color="inverse")
    if total_tasks > 0:
        m4.metric("Hiệu suất", f"{int((done_tasks/total_tasks)*100)}%")
    else:
        m4.metric("Hiệu suất", "0%")
    
    st.markdown("---")

    # 2. BẢNG TƯƠNG TÁC DỮ LIỆU (DATA EDITOR) - Đã xóa phần trùng lặp
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

    # 3. CẢNH BÁO NHẮC NHỞ & QUÁ HẠN DEADLINE
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

    # 4. DASHBOARD BÁO CÁO (BIỂU ĐỒ)
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
# TAB 2: GỬI MAIL PRE-ALERT KÈM CHỨNG TỪ
# ==========================================
with tab_mail:
    st.subheader("📸 Quét mã QR/Barcode")
    scanned_data = st.text_input("Nhập mã QR (hoặc dùng súng quét mã vạch tại đây):", placeholder="Quét mã tại đây...")
    if scanned_data:
        st.success(f"Đã nhận diện hàng hóa: {scanned_data}")
        st.info("Hệ thống đã nhận diện mã hàng, đang lấy dữ liệu từ Server...")
        
    st.markdown("---")
    st.subheader("📎 Gửi thông báo kèm chứng từ")
    
    colA, colB = st.columns(2)
    with colA:
        receiver_email = st.text_input("Gửi đến (To - Bắt buộc):")
    with colB:
        cc_email = st.text_input("Đồng gửi (CC - Tùy chọn):")
        
    col1, col2, col3 = st.columns(3)
    booking_no = col1.text_input("Số Booking:", "BKG-VNM-998877")
    container_no = col2.text_input("Số Container:", "CMAU1234567")
    cut_off = col3.text_input("Cut-off:", "17:00 - 25/06/2026")
    
    # Nút Upload File đính kèm (Đã đồng bộ tên biến)
    uploaded_file = st.file_uploader("Tải ảnh chứng từ lên (JPG, PNG, PDF):", type=['jpg', 'jpeg', 'png', 'pdf'])
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 XÁC NHẬN GỬI THÔNG BÁO MÀ KHÔNG BẮT BUỘC ẢNH"):
        if not receiver_email:
            st.error("⚠️ Vui lòng điền Email người nhận (To)!")
        else:
            with st.spinner('Hệ thống đang tự động gửi email và tệp tin...'):
                try:
                    # 1. TỰ ĐỘNG TẠO FILE BOOKING NOTE HTML ĐỂ ĐÍNH KÈM
                    file_name = f"Booking_Note_{booking_no}.html"
                    file_content = f"""
                    <html><body style="font-family: Arial, sans-serif; line-height: 1.6;">
                        <h2 style="text-align: center; color: #185ADB;">CÔNG TY TNHH LOGISTICS ELOGS</h2><hr>
                        <h3>THÔNG TIN ĐẶT CHỖ (BOOKING NOTE)</h3>
                        <p>Kính gửi Quý khách hàng/Bộ phận liên quan,</p>
                        <ul>
                            <li><b>Số Booking:</b> {booking_no}</li>
                            <li><b>Tên tàu / Chuyến:</b> EVER GIVEN / 042W</li>
                            <li><b>Số Container:</b> {container_no}</li>
                            <li><b>Thời gian Cut-off VGM/SI:</b> <span style="color: red; font-weight: bold;">{cut_off}</span></li>
                        </ul>
                    </body></html>
                    """
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write(file_content)

                    # 2. ĐÓNG GÓI PHONG BÌ EMAIL
                    msg = MIMEMultipart()
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = receiver_email
                    if cc_email: 
                        msg['Cc'] = cc_email
                    msg['Subject'] = f"[URGENT] Nhắc nhở Cut-off VGM/SI - Booking: {booking_no}"
                    
                    html_body = f"<html><body><h2>THÔNG BÁO ĐÃ CÓ LỊCH CUT-OFF</h2><p>Chi tiết lô hàng vui lòng xem tệp đính kèm phía dưới.</p></body></html>"
                    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

                    # 3. ĐÍNH KÈM FILE HTML BẮT BUỘC
                    with open(file_name, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename= {file_name}")
                    msg.attach(part)

                    # 4. ĐÍNH KÈM FILE TÙY CHỌN (NẾU CÓ TẢI LÊN)
                    if uploaded_file is not None:
                        file_data = uploaded_file.read()
                        file_part = MIMEBase("application", "octet-stream")
                        file_part.set_payload(file_data)
                        encoders.encode_base64(file_part)
                        file_part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                        msg.attach(file_part)

                    # 5. TIẾN HÀNH GỬI
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(SENDER_EMAIL, APP_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    
                    st.success("🎉 TUYỆT VỜI! Email thông báo cùng file đính kèm đã gửi thành công!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Lỗi gửi mail: {e}. Vui lòng kiểm tra tài khoản cấu hình.")
