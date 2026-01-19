# -*- coding: utf-8 -*-
"""
APP CHẤM ĐIỂM THI ĐUA - Streamlit Cloud Optimized
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==================== CẤU HÌNH ====================
st.set_page_config(
    page_title="Chấm Điểm Thi Đua",
    page_icon="📊",
    layout="wide"
)

# ==================== HÀM CHÍNH ====================
def main():
    st.title("📊 ỨNG DỤNG CHẤM ĐIỂM THI ĐUA")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ CÀI ĐẶT")
        heso_cc = st.slider("Hệ số chuyên cần", 0.0, 1.0, 0.3, 0.1)
        heso_tt = st.slider("Hệ số thành tích", 0.0, 1.0, 0.7, 0.1)
        st.info(f"Tổng hệ số: {heso_cc + heso_tt}")
    
    # Tab chính
    tab1, tab2 = st.tabs(["📤 Upload & Tính toán", "📊 Kết quả"])
    
    with tab1:
        # Upload file
        uploaded_file = st.file_uploader("Chọn file Excel", type=['xlsx', 'xls', 'csv'])
        
        if uploaded_file:
            try:
                # Đọc file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Đã tải: {uploaded_file.name}")
                
                # Hiển thị dữ liệu
                st.subheader("Dữ liệu đầu vào")
                st.dataframe(df.head())
                
                # Chọn cột
                col1, col2, col3 = st.columns(3)
                with col1:
                    col_hoten = st.selectbox("Cột Họ tên", df.columns)
                with col2:
                    col_chuyencan = st.selectbox("Cột Chuyên cần", df.columns)
                with col3:
                    col_thanhtich = st.selectbox("Cột Thành tích", df.columns)
                
                # Tính toán
                if st.button("🚀 TÍNH ĐIỂM", type="primary"):
                    # Tính điểm
                    df_result = df.copy()
                    
                    # Chuyển sang số
                    df_result[col_chuyencan] = pd.to_numeric(df_result[col_chuyencan], errors='coerce').fillna(0)
                    df_result[col_thanhtich] = pd.to_numeric(df_result[col_thanhtich], errors='coerce').fillna(0)
                    
                    # Tính điểm tổng
                    df_result['Điểm_tổng'] = (
                        df_result[col_chuyencan] * heso_cc +
                        df_result[col_thanhtich] * heso_tt
                    ).round(2)
                    
                    # Xếp loại
                    def phan_loai(diem):
                        if diem >= 90: return "Xuất sắc"
                        elif diem >= 80: return "Tốt"
                        elif diem >= 65: return "Khá"
                        elif diem >= 50: return "Trung bình"
                        else: return "Yếu"
                    
                    df_result['Xếp_loại'] = df_result['Điểm_tổng'].apply(phan_loai)
                    
                    # Sắp xếp
                    df_result = df_result.sort_values('Điểm_tổng', ascending=False)
                    df_result = df_result.reset_index(drop=True)
                    df_result.index = df_result.index + 1
                    
                    # Lưu vào session
                    st.session_state['df_result'] = df_result
                    st.session_state['col_hoten'] = col_hoten
                    
                    st.success("✅ Tính toán thành công! Chuyển tab Kết quả")
                    
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
    
    with tab2:
        if 'df_result' in st.session_state:
            df_result = st.session_state['df_result']
            col_hoten = st.session_state['col_hoten']
            
            # Hiển thị kết quả
            st.subheader("🏆 Kết quả thi đua")
            st.dataframe(df_result[[col_hoten, 'Điểm_tổng', 'Xếp_loại']].head(20))
            
            # Xuất file
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_result.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 TẢI KẾT QUẢ",
                data=excel_buffer.getvalue(),
                file_name=f"ket_qua_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("👈 Vui lòng tính toán ở tab đầu tiên")

# ==================== CHẠY APP ====================
if __name__ == "__main__":
    main()