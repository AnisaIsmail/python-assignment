import streamlit as st
import pandas as pd
import os
from io import BytesIO
import numpy as np
from scipy.stats import zscore

st.set_page_config(page_title="Advanced Data Sweeper", layout="wide")

# Dark/Light Mode Toggle
mode = st.radio("Select Mode", ["Light Mode", "Dark Mode"], key="mode")

# Language selector
language = st.selectbox("Select Language", ["English", "Chinese"])

# Set text based on selected language
if language == "English":
    title_text = "Advanced Data Sweeper"
    description_text = "Transform your files between CSV and Excel formats with built-in data cleaning and visualization."
    file_prompt = "Upload your files (CSV or Excel):"
    columns_prompt = "🎯 Select Columns to Convert"
    visualize_prompt = "📊 Customize Visualization"
    insight_prompt = "Generate Data Insights"
    conversion_prompt = "🔄 Conversion Options"
    success_message = "🎉 All files processed successfully!"
else:
    title_text = "高级数据清洁工具"
    description_text = "将您的文件在CSV和Excel格式之间转换，并提供内置的数据清理和可视化功能。"
    file_prompt = "上传您的文件（CSV或Excel）："
    columns_prompt = "🎯 选择要转换的列"
    visualize_prompt = "📊 自定义可视化"
    insight_prompt = "生成数据洞察"
    conversion_prompt = "🔄 转换选项"
    success_message = "🎉 所有文件处理成功！"

# Apply dynamic styling based on mode
if mode == "Light Mode":
    st.markdown("""
    <style>
        .main { background-color: white; }
        .block-container { background-color: #f4f4f9; color: black; }
        h1, h2, h3, h4, h5, h6 { color: #0078D7; }
        .stButton>button { background-color: #0078D7; color: white; }
        .stButton>button:hover { background-color: #005a9e; }
        .stDownloadButton>button { background-color: #28a745; color: white; }
        .stDownloadButton>button:hover { background-color: #218838; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .main { background-color: #121212; }
        .block-container { background-color: #1e1e1e; color: white; }
        h1, h2, h3, h4, h5, h6 { color: #66c2ff; }
        .stButton>button { background-color: #0078D7; color: white; }
        .stButton>button:hover { background-color: #005a9e; }
        .stDownloadButton>button { background-color: #28a745; color: white; }
        .stDownloadButton>button:hover { background-color: #218838; }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title(title_text)
st.write(description_text)

# File uploader
uploaded_files = st.file_uploader(file_prompt, type=["csv", "xlsx"], accept_multiple_files=True)

# Processing uploaded files
if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()

        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue

        # Display file information
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")
        
        # Preview the uploaded file
        st.write("🔍 Preview of the Uploaded File:")
        st.dataframe(df.head())

        # Column selection for conversion
        st.subheader(columns_prompt)
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Visualization options
        st.subheader(visualize_prompt)
        visualization_type = st.radio("Select Chart Type", ["Bar Chart", "Line Chart"])

        if visualization_type == "Bar Chart":
            x_col = st.selectbox("Select X-axis", df.columns)
            y_col = st.selectbox("Select Y-axis", df.select_dtypes(include='number').columns)
            st.bar_chart(df[[x_col, y_col]])

        elif visualization_type == "Line Chart":
            x_col = st.selectbox("Select X-axis", df.columns)
            y_col = st.selectbox("Select Y-axis", df.select_dtypes(include='number').columns)
            st.line_chart(df[[x_col, y_col]])

        # AI Insights
        if st.checkbox(f"Generate Data Insights for {file.name}"):
            st.subheader("🔎 Basic Statistical Insights")
            st.write(df.describe())

            # Handle outliers
            z_scores = np.abs(zscore(df.select_dtypes(include=np.number)))
            outliers = (z_scores > 3).all(axis=1)
            st.write(f"Outliers Detected: {sum(outliers)} rows")

            st.subheader("🔗 Correlation Matrix")
            # Filter out non-numeric columns before calculating correlation
            numeric_df = df.select_dtypes(include=[np.number])
            st.write(numeric_df.corr())

        # File conversion options
        st.subheader(conversion_prompt)
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index= False)
                file_name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index= False, engine='openpyxl')
                file_name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            
            # Download button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

# Final success message
st.success(success_message)