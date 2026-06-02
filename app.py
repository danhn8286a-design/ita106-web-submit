import os
import time
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. CẤU HÌNH TRANG & SEO (META DATA)
# ==========================================
st.set_page_config(
    page_title="ITA106 - Hệ Thống Nộp Bài Tập Lab",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Thư mục lưu trữ file nộp
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Dữ liệu giả lập về Deadline của các bài Lab
LAB_DATA = {
    f"Lab {i}": {
        "title": f"ITA106_Lab {i}: Thực hành tổng hợp Bài {i}",
        "deadline": f"23:59 - 15/06/2026",
        "max_size": "20 MB",
    }
    for i in range(1, 9)
}

# ==========================================
# 2. UI/UX CUSTOM CSS (GOOGLE DRIVE STYLE)
# ==========================================
st.markdown(
    """
    <style>
        /* Toàn bộ font chữ và nền tối giản */
        html, body, [data-testid="stSidebar"] {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #F8F9FA;
        }
        
        /* Tùy chỉnh thanh Sidebar điều hướng */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E0E0E0;
        }
        
        /* Làm đẹp các tiêu đề */
        h1 {
            color: #1A73E8 !important; /* Xanh Google */
            font-weight: 600 !important;
        }
        h2, h3 {
            color: #3C4043 !important;
            font-weight: 500 !important;
        }
        
        /* Tùy chỉnh vùng kéo thả file */
        [data-testid="stFileUploader"] {
            border: 2px dashed #1A73E8 !important;
            border-radius: 8px !important;
            background-color: #F1F3F4 !important;
            padding: 10px;
        }
        
        /* Định dạng bảng giống Google Drive */
        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 14px;
            min-width: 400px;
        }
        .styled-table th {
            background-color: #F1F3F4;
            color: #5F6368;
            text-align: left;
            padding: 12px 15px;
            font-weight: 500;
            border-bottom: 1px solid #E0E0E0;
        }
        .styled-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #E0E0E0;
            color: #3C4043;
        }
        .styled-table tr:hover {
            background-color: #F8F9FA;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 3. HÀM XỬ LÝ LOGIC (PERFORMANCE OPTIMIZED)
# ==========================================
def get_file_size_format(b):
    """Tối ưu hiển thị kích thước file trực quan"""
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024.0:
            return f"{b:.1f} {unit}"
        b /= 1024.0


def get_history_log(lab_name):
    """Lấy danh sách file đã nộp của Lab hiện tại"""
    lab_folder = os.path.join(UPLOAD_DIR, lab_name)
    if not os.path.exists(lab_folder):
        return []

    files_list = []
    for filename in os.listdir(lab_folder):
        file_path = os.path.join(lab_folder, filename)
        if os.path.isfile(file_path):
            stat_info = os.stat(file_path)
            mod_time = datetime.fromtimestamp(stat_info.st_mtime).strftime(
                "%d/%m/%Y %H:%M:%S"
            )
            size = get_file_size_format(stat_info.st_size)
            files_list.append(
                {"Tên": filename, "Ngày sửa đổi": mod_time, "Kích cỡ tệp": size}
            )
    return files_list


# ==========================================
# 4. GIAO DIỆN NGƯỜI DÙNG (UI/UX)
# ==========================================

# --- SIDEBAR: Thanh điều hướng danh sách bài Lab ---
with st.sidebar:
    st.markdown(
        "<h2 style='text-align: center; color: #1A73E8;'>📁 ITA106 Drive</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("### 📑 Danh sách bài Lab")

    # Chọn bài Lab (Tương đương việc click chọn thư mục trong Google Drive)
    selected_lab = st.radio(
        label="Chọn bài Lab để nộp:",
        options=[f"Lab {i}" for i in range(1, 9)],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Sinh viên lưu ý nộp bài đúng hạn. Hệ thống tự động ghi nhận.")

# --- TRANG CHÍNH: Khu vực hiển thị thông tin & Nộp bài ---
# SEO - H1 Standard Header
st.markdown(
    f"<h1>Hệ thống nộp bài: {LAB_DATA[selected_lab]['title']}</h1>",
    unsafe_allow_html=True,
)

# Khối thông tin Metadata của Bài Lab
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.markdown(
        f"⏳ **Hạn chót (Deadline):** <span style='color: #D93025; font-weight: bold;'>{LAB_DATA[selected_lab]['deadline']}</span>",
        unsafe_allow_html=True,
    )
with col_info2:
    st.markdown(
        f"📦 **Dung lượng tối đa:** `{LAB_DATA[selected_lab]['max_size']}`"
    )

st.markdown("---")

# Khu vực Nộp bài (Upload)
st.markdown("### 📤 Tải tệp lên")
uploaded_file = st.file_uploader(
    "Kéo và thả file của bạn vào đây hoặc bấm để chọn file",
    type=["pdf", "docx", "zip", "rar"],
    accept_files_to_select=False,
    label_visibility="collapsed",
)

if uploaded_file is not None:
    # 1. Trạng thái phản hồi (Feedback) - Thanh tiến trình giả lập tăng trải nghiệm UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    for percent_complete in range(0, 101, 20):
        time.sleep(0.1)  # Giả lập thời gian tải lên
        progress_bar.progress(percent_complete)
        status_text.text(f"Đang tải lên: {percent_complete}%")

    # 2. Tiến hành lưu file thực tế vào ổ đĩa
    lab_upload_path = os.path.join(UPLOAD_DIR, selected_lab)
    if not os.path.exists(lab_upload_path):
        os.makedirs(lab_upload_path)

    target_path = os.path.join(lab_upload_path, uploaded_file.name)

    try:
        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Thông báo thành công màu xanh theo tiêu chuẩn UI/UX
        st.success(f"✔️ Thành công: Đã nộp tệp '{uploaded_file.name}'!")
        status_text.empty()
        progress_bar.empty()
    except Exception as e:
        # Thông báo thất bại màu đỏ
        st.error(f"❌ Thất bại: Không thể nộp file. Lỗi: {e}")

st.markdown("---")

# --- LỊCH SỬ NỘP BÀI (BẢNG KIỂU GOOGLE DRIVE) ---
st.markdown("### 📜 Lịch sử tệp đã nộp")

history_data = get_history_log(selected_lab)

if history_data:
    # Chuyển đổi sang HTML để custom giao diện giống hệt mẫu yêu cầu
    df = pd.DataFrame(history_data)

    html_table = "<table class='styled-table'><thead><tr>"
    for col in df.columns:
        html_table += f"<th>{col}</th>"
    html_table += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html_table += f"<tr><td>📄 {row['Tên']}</td><td>{row['Ngày sửa đổi']}</td><td>{row['Kích cỡ tệp']}</td></tr>"
    html_table += "</tbody></table>"

    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.info("Chưa có tệp nào được nộp cho bài Lab này.")