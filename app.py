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
    .stApp { background-color: #f4f7f6; }
    
    [data-testid="stSidebar"] { background-color: #0A2647; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] { gap: 12px; }
    [data-testid="stSidebar"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.06); 
        padding: 12px 20px; border-radius: 16px !important; 
        border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s ease; cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15); transform: translateX(6px); border-color: rgba(255,255,255,0.3);
    }
    [data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] > div:first-child { display: none; }
    [data-testid="stSidebar"] .stRadio div[data-baseweb="radio"] { width: 100%; }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e4e8; padding: 22px;
        border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); transition: transform 0.2s ease-in-out, box-shadow 0.2s;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }
    
    .stDataFrame { border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    
    div.stButton > button { 
        background-color: #185ADB !important; color: white !important; border-radius: 20px !important; 
        font-weight: 600 !important; border: none !important; padding: 10px 24px !important; transition: all 0.3s ease;
    }
    div.stButton > button:hover { 
        background-color: #0A2647 !important; box-shadow: 0 4px 12px rgba(24, 90, 219, 0.3) !important; transform: translateY(-2px);
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif !important; }
    h1, h2, h3 { color: #0A2647 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO KHO DỮ LIỆU & QUẢN LÝ TRẠNG THÁI ---
if 'tasks_df' not in st.session_state:
    st.session_state.tasks_df = pd.DataFrame({
        "🚩 Quan trọng": [True, False],
        "📌 Tên công việc": ["Khai E-port lô BKG-123", "Gửi SI hãng tàu Evergreen"],
        "🏷️ Nhãn": ["Hàng Nhập", "Chứng Từ"],
        "⏳ Trạng thái": ["Đang làm", "Chưa làm"],
        "📅 Deadline": [date(2026, 6, 30), date(2026, 6, 30)], 
        "💬 Ghi chú": ["Sếp dặn check kỹ số container", ""]
    })
    # Khởi tạo bản nháp và định vị Tab hiện tại
    st.session_state.temp_edited_df = st.session_state.tasks_df
    st.session_state.current_tab = "📊 Tổng quan (Dashboard)"

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

# ✨ THUẬT TOÁN ĐỒNG BỘ: Chỉ cập nhật dữ liệu gốc khi chuyển Tab
if menu != st.session_state.current_tab:
    st.session_state.tasks_df = st.session_state.temp_edited_df
    st.session_state.current_tab = menu

st.sidebar.markdown("---")
st.sidebar.info("💡 **Giao diện 4.0:** Bảng công việc đã được xử lý chống giật lag, thêm việc mới mượt mà không bị mất dòng.")

# ==========================================
# MÀN HÌNH 1: DASHBOARD
# ==========================================
if menu == "📊 Tổng quan (Dashboard)":
    st.title("Hiệu suất Công việc hôm nay")
    st.markdown("Theo dõi và cập nhật tiến độ các lô hàng theo thời gian thực.")
    
    # 1. TẠO VÙNG CHỨA GIỮ CHỖ CHO THỐNG KÊ (Để in ra ở trên cùng)
    metrics_container = st.container()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. HIỂN THỊ BẢNG (Xử lý trước để có dữ liệu mới nhất)
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
    # Lưu vào nháp, tuyệt đối KHÔNG ghi đè trực tiếp lên tasks_df ở đây
    st.session_state.temp_edited_df = edited_df

    # 3. ĐIỀN DỮ LIỆU LÊN VÙNG CHỨA PHÍA TRÊN
    with metrics_container:
        total_tasks = len(edited_df)
        done_tasks = len(edited_df[edited_df["⏳ Trạng thái"] == "Hoàn thành"])
        important_tasks = len(edited_df[edited_df["🚩 Quan trọng"] == True])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📦 Tổng số Việc", total_tasks)
        m2.metric("✅ Đã hoàn thành", done_tasks)
        m3.metric("🔥 Cần xử lý gấp", important_tasks, delta_color="inverse")
        m4.metric("📈 Hiệu suất", f"{int((done_tasks/total_tasks)*100)}%" if total_tasks > 0 else "0%")

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
        
        scanned_data = st.text_input("Nhập mã Booking cần kiểm tra:", placeholder="Ví dụ: MSK-999").strip()
        
        if st.button("Kích hoạt Tra cứu Hệ thống"):
            if scanned_data:
                with st.spinner('Đang kết nối API và đồng bộ hóa đám mây...'):
                    time.sleep(1.2) 
                    
                    logistics_data = {
                        "BKG-123": {
                            "Mã Vận Đơn": "BKG-123", "Hãng Tàu": "EVERGREEN LINES", 
                            "Tàu vận chuyển": "EVER GIVEN / 0244E", "Trạng thái": "On Board (Đã lên tàu)", 
                            "Cảng xếp hàng (POL)": "Cát Lái (VNSGN)", "Cảng dỡ hàng (POD)": "Rotterdam (NLRTM)"
                        },
                        "MSK-999": {
                            "Mã Vận Đơn": "MSK-999", "Hãng Tàu": "MAERSK LINE", 
                            "Tàu vận chuyển": "MAERSK ESSEN / 261W", "Trạng thái": "Customs Hold (Đang giữ kiểm hóa)", 
                            "Cảng xếp hàng (POL)": "Cái Mép (VNCMPT)", "Cảng dỡ hàng (POD)": "Los Angeles (USLAX)"
                        },
                        "CMA-555": {
                            "Mã Vận Đơn": "CMA-555", "Hãng Tàu": "CMA CGM", 
                            "Tàu vận chuyển": "CMA CGM LOGISTICS / 09B", "Trạng thái": "Pending (Chờ duyệt hạ bãi)", 
                            "Cảng xếp hàng (POL)": "Hải Phòng (VNHPH)", "Cảng dỡ hàng (POD)": "Singapore (SGSIN)"
                        },
                        "MSC-777": {
                            "Mã Vận Đơn": "MSC-777", "Hãng Tàu": "MSC SHIPPING CO", 
                            "Tàu vận chuyển": "MSC OSCAR / 115S", "Trạng thái": "Leave Behind (Bị rớt tàu do quá hạn)", 
                            "Cảng xếp hàng (POL)": "Cát Lái (VNSGN)", "Cảng dỡ hàng (POD)": "Hamburg (DEHAM)"
                        },
                        "VNM-888": {
                            "Mã Vận Đơn": "VNM-888", "Hãng Tàu": "SÀN VẬN TẢI NỘI ĐỊA ELOGS", 
                            "Tàu vận chuyển": "Xe Tải Tuyến Bắc Nam / 29C-11234", "Trạng thái": "In Transit (Xe đang di chuyển)", 
                            "Cảng xếp hàng (POL)": "Kho Vinamilk Bình Dương", "Cảng dỡ hàng (POD)": "Kho Tổng Vinamilk Hà Nội"
                        }
                    }
                    
                    if scanned_data in logistics_data:
                        res = logistics_data[scanned_data]
                        st.success("🎉 Kết nối hệ thống API thành công!")
                        
                        status_str = res["Trạng thái"]
                        bg_badge, text_badge = "#e2f0d9", "#385723" 
                        
                        if "On Board" in status_str: bg_badge, text_badge = "#d4edda", "#155724"
                        elif "Hold" in status_str: bg_badge, text_badge = "#fff3cd", "#856404" 
                        elif "Pending" in status_str: bg_badge, text_badge = "#cce5ff", "#004085" 
                        elif "Leave Behind" in status_str: bg_badge, text_badge = "#f8d7da", "#721c24" 
                        elif "In Transit" in status_str: bg_badge, text_badge = "#e0f7fa", "#006064" 
                        
                        html_card = f"<div style='background-color: #ffffff; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid #e3e8ee; margin-top: 15px; margin-bottom: 15px;'><div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f4f7f6; padding-bottom: 15px; margin-bottom: 20px;'><div><span style='font-size: 11px; color: #a0aec0; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;'>Mã số quản lý vận đơn</span><h3 style='margin: 0; color: #0A2647; font-size: 24px; font-weight: 700;'>{res['Mã Vận Đơn']}</h3></div><div style='background-color: {bg_badge}; color: {text_badge}; padding: 8px 18px; border-radius: 24px; font-weight: 700; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;'>● {status_str}</div></div><div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px;'><div style='background-color: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #edf2f7;'><span style='font-size: 11px; color: #718096; font-weight: 600; text-transform: uppercase;'>Hãng Tàu (Carrier)</span><div style='font-size: 15px; color: #1a202c; font-weight: 700; margin-top: 4px;'>{res['Hãng Tàu']}</div></div><div style='background-color: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #edf2f7;'><span style='font-size: 11px; color: #718096; font-weight: 600; text-transform: uppercase;'>Phương tiện (Vessel/Voy/Truck)</span><div style='font-size: 15px; color: #1a202c; font-weight: 700; margin-top: 4px; font-family: monospace;'>{res['Tàu vận chuyển']}</div></div><div style='background-color: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #edf2f7;'><span style='font-size: 11px; color: #718096; font-weight: 600; text-transform: uppercase;'>Cảng xếp hàng (POL)</span><div style='font-size: 15px; color: #1a202c; font-weight: 700; margin-top: 4px;'>{res['Cảng xếp hàng (POL)']}</div></div><div style='background-color: #f8fafc; padding: 16px; border-radius: 12px; border: 1px solid #edf2f7;'><span style='font-size: 11px; color: #718096; font-weight: 600; text-transform: uppercase;'>Cảng dỡ hàng (POD)</span><div style='font-size: 15px; color: #1a202c; font-weight: 700; margin-top: 4px;'>{res['Cảng dỡ hàng (POD)']}</div></div></div></div>"
                        
                        st.markdown(html_card, unsafe_allow_html=True)
                        
                        with st.expander("🛠️ Nhấn để xem Chuỗi dữ liệu API gốc (JSON Payload)"):
                            st.json(logistics_data[scanned_data])
                    else:
                        st.error(f"❌ Lỗi [404]: Không tìm thấy dữ liệu vận đơn cho mã '{scanned_data}' trên hệ thống!")
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
        
        uploaded_file = st.file_uploader("Đính kèm tệp chứng từ bổ sung (Hình ảnh, PDF):")
        
        if st.button("🚀 PHÁT HÀNH EMAIL THÔNG BÁO"):
            if not receiver_email:
                st.error("⚠️ Bạn chưa điền địa chỉ Email người nhận!")
            else:
                with st.spinner('Đang đóng gói chứng từ và gửi SMTP...'):
                    try:
                        file_name = f"Booking_Note_{booking_no}.html"
                        file_content = f"""
                        <html>
                        <head>
                            <style>
                                body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #2B3A42; margin: 30px; background-color: #ffffff; line-height: 1.6; }}
                                .header {{ border-bottom: 3px solid #0A2647; padding-bottom: 12px; margin-bottom: 25px; }}
                                .company-name {{ color: #0A2647; font-size: 22px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }}
                                .company-info {{ font-size: 13px; color: #666666; margin-top: 4px; }}
                                .doc-title {{ text-align: center; color: #185ADB; font-size: 24px; font-weight: 700; margin: 35px 0 10px 0; text-transform: uppercase; letter-spacing: 1px; }}
                                .doc-subtitle {{ text-align: center; font-size: 14px; color: #555555; font-style: italic; margin-bottom: 35px; }}
                                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }}
                                th, td {{ border: 1px solid #d1d9e6; padding: 14px 18px; font-size: 14px; text-align: left; }}
                                th {{ background-color: #0A2647; color: #ffffff; font-weight: 600; text-transform: uppercase; width: 35%; letter-spacing: 0.5px; }}
                                td {{ background-color: #fcfdfe; }}
                                .highlight {{ color: #d9534f; font-weight: 700; font-size: 16px; background-color: #fff9f9; }}
                                .notes-section {{ background-color: #f8f9fa; border-left: 4px solid #185ADB; padding: 18px; border-radius: 0 8px 8px 0; font-size: 13px; margin-top: 40px; }}
                                .notes-title {{ font-weight: 700; color: #0A2647; margin-bottom: 8px; font-size: 14px; }}
                                .signature {{ margin-top: 50px; text-align: right; font-weight: 700; color: #0A2647; font-size: 14px; padding-right: 20px; }}
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <div class="company-name">⚓ ELOGS LOGISTICS CO., LTD</div>
                                <div class="company-info">
                                    <b>Trụ sở:</b> Tòa nhà Landmark, Tầng 18, Quận 1, TP. Hồ Chí Minh, Việt Nam<br>
                                    <b>Hotline:</b> (+84) 1900 ELOGS | <b>Email:</b> ops@elogs-workspace.com
                                </div>
                            </div>
                            
                            <div class="doc-title">THÔNG BÁO LỊCH TRÌNH LÔ HÀNG & HẠN CHÓT</div>
                            <div class="doc-subtitle">(OFFICIAL SHIPMENT & CUT-OFF NOTICE)</div>
                            
                            <table>
                                <tr>
                                    <th>Mã số Vận đơn (Booking No.)</th>
                                    <td><b style="font-size: 16px; color: #185ADB;">{booking_no}</b></td>
                                </tr>
                                <tr>
                                    <th>Ký hiệu Container (Container No.)</th>
                                    <td><span style="font-family: monospace; font-size: 15px; font-weight: 600;">{container_no}</span></td>
                                </tr>
                                <tr>
                                    <th>Hạn chót hạ bãi (Cut-off Time)</th>
                                    <td class="highlight">⚠️ {cut_off}</td>
                                </tr>
                                <tr>
                                    <th>Trạng thái chứng từ (Status)</th>
                                    <td><span style="color: #5cb85c; font-weight: bold; background-color: #f2fbf2; padding: 4px 10px; border-radius: 12px; font-size: 12px;">ĐÃ PHÁT HÀNH (ORIGINAL SENT)</span></td>
                                </tr>
                                <tr>
                                    <th>Thời gian xuất bản (Issue Date)</th>
                                    <td>{datetime.now().strftime('%d/%m/%Y - %H:%M')}</td>
                                </tr>
                            </table>
                            
                            <div class="notes-section">
                                <div class="notes-title">⚠️ ĐIỀU KHOẢN VÀ LƯU Ý QUAN TRỌNG (OPERATIONAL TERMS):</div>
                                1. Quý khách vui lòng hoàn thành toàn bộ thủ tục thông quan hải quan và hạ bãi trước thời gian <b>Cut-off</b> quy định phía trên.<br>
                                2. Mọi sự chậm trễ dẫn đến việc rớt tàu (Leave behind), ELOGS sẽ không chịu trách nhiệm đối với các chi phí phát sinh lưu kho bãi (DEM/DET).<br>
                                3. Nếu có bất kỳ thay đổi hoặc sự cố phát sinh, vui lòng liên hệ ngay với bộ phận Điều độ của chúng tôi qua Hotline hoặc Email ở phần đầu văn bản.
                            </div>
                            
                            <div class="signature">
                                TRÂN TRỌNG CẢM ƠN!<br>
                                <span style="font-weight: 500; font-style: italic; color: #666666; font-size: 13px;">Bộ phận Chứng từ & Hiện trường ELOGS Operations</span>
                            </div>
                        </body>
                        </html>
                        """
                        
                        with open(file_name, "w", encoding="utf-8") as f: f.write(file_content)

                        msg = MIMEMultipart()
                        msg['From'], msg['To'], msg['Subject'] = SENDER_EMAIL, receiver_email, f"[URGENT] Lịch Cut-off lô hàng {booking_no}"
                        if cc_email: msg['Cc'] = cc_email
                        msg.attach(MIMEText("Kính gửi quý đối tác,\n\nHệ thống ELOGS gửi đến bạn file chứng từ Thông báo lịch trình và hạn chót (Cut-off Notice) chính thức đính kèm bên dưới.\nVui lòng kiểm tra và hoàn tất thủ tục đúng hạn.\n\nTrân trọng!", 'plain', 'utf-8'))

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
                        st.success("🎉 Chứng từ chuyên nghiệp đã đóng gói và gửi thành công đến đối tác!")
                    except Exception as e:
                        st.error(f"❌ Gặp sự cố khi gửi thư qua Gmail: {e}")

# ==========================================
# MÀN HÌNH 3: CÀI ĐẶT
# ==========================================
elif menu == "⚙️ Cài đặt hệ thống":
    st.title("⚙️ Cài đặt Hệ thống")
    st.info("Tính năng phân quyền đại lý, kết nối API nhà xe và thiết lập thông số EDI sẽ xuất hiện trong bản cập nhật lớn tiếp theo.")
