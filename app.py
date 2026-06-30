import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
# --- HÀM TỰ ĐỘNG HÓA (MÔ PHỎNG BACKEND LOGIC) ---
import requests # Thư viện dùng để gọi API

def auto_assign_task(task_name, priority_level):
    """
    Hàm gọi API thực tế lên máy chủ AWS.
    """
    # 1. Đường link API (Endpoint) do AWS cung cấp cho bạn
    # (Bạn sẽ lấy link này từ AWS API Gateway)
    aws_api_url = "https://ab12cd34ef.execute-api.ap-southeast-1.amazonaws.com/prod/tao-cong-viec"
    
    # 2. Gói dữ liệu bạn muốn gửi cho AWS
    payload = {
        "task_name": task_name,
        "priority": priority_level
    }
    
    try:
        # 3. Gửi yêu cầu (POST request) lên AWS
        response = requests.post(aws_api_url, json=payload)
        
        # 4. Kiểm tra xem AWS có trả lời thành công không (Mã 200 là Thành công)
        if response.status_code == 200:
            # AWS xử lý xong và trả về dữ liệu của task mới
            # Ví dụ: AWS sẽ trả về: {"🚩 Quan trọng": True, "📌 Tên công việc": "...", ...}
            new_task_from_aws = response.json()
            
            # Cập nhật dữ liệu từ AWS vào bảng của Streamlit
            st.session_state.tasks_df = pd.concat(
                [st.session_state.tasks_df, pd.DataFrame([new_task_from_aws])], 
                ignore_index=True
            )
            return True
        else:
            # Nếu AWS báo lỗi (ví dụ: máy chủ sập, sai định dạng)
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
    /* Bo tròn các khung thông tin */
    .stApp { background-color: #f5f7f9; }
    div.stButton > button { border-radius: 8px; border: 1px solid #ddd; }
    
    /* Làm nổi bật vùng Dashboard */
    .stDataFrame { border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    /* 1. Đổi Font chữ sang loại hiện đại (Inter, Roboto hoặc Sans-serif) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* 2. Làm thẻ Tab bo tròn và gọn gàng */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        background-color: #f1f3f6;
        padding: 10px 20px;
    }
    
    /* 3. Bo tròn góc các ô nhập liệu và bảng biểu */
    input, textarea, div[data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid #d1d9e6 !important;
    }
    
    /* 4. Nút bấm phẳng, bo tròn, màu xanh chuẩn SaaS */
    div.stButton > button {
        background-color: #2563eb !important; /* Xanh dương đậm chuẩn SaaS */
        color: white !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* 5. Giao diện nền trắng sáng sạch sẽ */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* 6. Tạo đổ bóng nhẹ cho các khối nội dung (Cards) */
    .stColumn {
        background-color: #ffffff;
        border: 1px solid #f0f0f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
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
        "📅 Deadline": [date.today(), date.today()], 
        "💬 Trao đổi / Ghi chú": ["Sếp dặn check kỹ số container", ""]
    })

st.title("🚢 HỆ THỐNG QUẢN LÝ LOGISTICS - ELOGS")

# SẮP XẾP LẠI TABS: Dashboard (Quản trị) lên trước, Gửi Email ra sau
tab_dashboard, tab_mail = st.tabs(["📊 QUẢN TRỊ CÔNG VIỆC (DASHBOARD)", "📧 PRE-ALERT & CHỨNG TỪ"])


# ==========================================
# TAB 1: DASHBOARD QUẢN TRỊ CÔNG VIỆC
# ==========================================
with tab_dashboard:
    st.subheader("Bảng Kế hoạch & Theo dõi tiến độ")
    
    # --- THÊM PHẦN TỰ ĐỘNG HÓA ---
    if st.button("🤖 Kích hoạt tạo Task tự động (Mô phỏng hệ thống)"):
        auto_assign_task("Kiểm tra hàng tồn kho mới nhập", "High")
        st.success("Hệ thống đã tự động thêm task mới!")
        st.rerun() # Refresh lại trang để cập nhật bảng
    
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

    # 2. BẢNG TƯƠNG TÁC DỮ LIỆU (DATA EDITOR)
    edited_df = st.data_editor(
        st.session_state.tasks_df,
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
        if isinstance(deadline, str): deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
        
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
    
    # Nút Upload File đính kèm
    uploaded_file = st.file_uploader("Tải ảnh chứng từ lên (JPG, PNG, PDF):", type=['jpg', 'jpeg', 'png', 'pdf'])
    
    if st.button("🚀 XÁC NHẬN GỬI THÔNG BÁO KÈM CHỨNG TỪ"):
        if not receiver_email:
            st.error("Vui lòng điền Email người nhận!")
        elif not uploaded_file:
            st.error("Vui lòng chọn tệp chứng từ đính kèm!")
        else:
            with st.spinner('Đang đóng gói và gửi mail...'):
                try:
                    msg = MIMEMultipart()
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = receiver_email
                    if cc_email: msg['Cc'] = cc_email
                    msg['Subject'] = f"[URGENT] Pre-alert Booking: {booking_no}"
                    msg.attach(MIMEText(f"Kính gửi bộ phận liên quan,<br>Vui lòng xem file đính kèm để hoàn tất thủ tục trước Cut-off: {cut_off}.", 'html'))
                    
                    # Đính kèm file
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(uploaded_file.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                    msg.attach(part)
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(SENDER_EMAIL, APP_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    st.success("🎉 TUYỆT VỜI! Đã gửi email kèm ảnh chứng từ thành công!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Lỗi: {e}")
