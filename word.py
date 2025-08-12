# 📦 Importing required libraries
import streamlit as st           # For creating the interactive web app
import pandas as pd              # For working with tables and CSV files
import numpy as np               # For numeric operations
from wordcloud import WordCloud, STOPWORDS  # For generating the word cloud
import matplotlib.pyplot as plt  # For displaying the word cloud as a plot
import PyPDF2                    # For reading PDF files
from docx import Document         # For reading Word (.docx) files
import plotly.express as px       # For interactive plotting (not used much here, but can be extended)
import base64                     # For encoding images/files for download
from io import BytesIO            # For saving plots in memory before download

# 📄 Function to read plain text (.txt) file
def read_txt(file):
    return file.getvalue().decode("utf-8")

# 📄 Function to read Word (.docx) file
def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])  # Join all paragraphs into one string

# 📄 Function to read PDF file
def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages])

# ✂️ Function to filter out stopwords (unwanted words like 'the', 'is', etc.)
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))  # Combine standard + user-added stopwords
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# 📥 Function to create a download link for an image
def get_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Plot as {format_}</a>'

# 📥 Function to create a download link for a DataFrame as CSV
def get_table_download_link(df, filename, file_label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'

# 🌟 Streamlit App Title
st.title("Word Cloud Generator")
st.subheader("📁 Upload a PDF, DOCX, or TXT file to generate a word cloud")

# 📤 File uploader
uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])
# st.set_option('deprecation.showPyplotGlobalUse', False)  # Avoids warnings

# 📂 If file is uploaded, process it
if uploaded_file:
    # Show file details
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)

    # Read file depending on type
    if uploaded_file.type == "text/plain":
        text = read_txt(uploaded_file)
    elif uploaded_file.type == "application/pdf":
        text = read_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = read_docx(uploaded_file)
    else:
        st.error("❌ File type not supported. Please upload a TXT, PDF, or DOCX file.")
        st.stop()

    # 📊 Create word count table (before filtering stopwords)
    words = text.split()
    word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)

    # 📌 Sidebar stopword selection
    use_standard_stopwords = st.sidebar.checkbox("Use standard stopwords?", True)
    top_words = word_count['Word'].head(50).tolist()
    additional_stopwords = st.sidebar.multiselect("Additional stopwords:", sorted(top_words))

    if use_standard_stopwords:
        all_stopwords = STOPWORDS.union(set(additional_stopwords))
    else:
        all_stopwords = set(additional_stopwords)

    # Remove stopwords from text
    text = filter_stopwords(text, all_stopwords)

    # 🖼️ If text is not empty after filtering
    if text:
        # 🎛️ Sidebar sliders for Word Cloud size
        width = st.sidebar.slider("Select Word Cloud Width", 400, 2000, 1200, 50)
        height = st.sidebar.slider("Select Word Cloud Height", 200, 2000, 800, 50)

        # 🌈 Generate the Word Cloud
        st.subheader("Generated Word Cloud")
        fig, ax = plt.subplots(figsize=(width/100, height/100))  # Convert pixels to inches
        wordcloud_img = WordCloud(
            width=width, height=height, background_color='white',
            max_words=200, contour_width=3, contour_color='steelblue'
        ).generate(text)

        ax.imshow(wordcloud_img, interpolation='bilinear')
        ax.axis('off')  # Hide axis
        st.pyplot(fig)

        # 💾 Save plot options
        format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
        resolution = st.slider("Select Resolution", 100, 500, 300, 50)

        if st.button(f"Save as {format_}"):
            buffered = BytesIO()
            plt.savefig(buffered, format=format_, dpi=resolution)
            st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

        # 📊 Word Count Table after stopwords removal
        st.subheader("Word Count Table")
        words = text.split()
        word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)
        st.write(word_count)

        # 📥 Download Word Count Table
        if st.button('Download Word Count Table as CSV'):
            st.markdown(get_table_download_link(word_count, "word_count.csv", "Click Here to Download"), unsafe_allow_html=True)

    # ℹ️ Sidebar info
    # st.sidebar.markdown("---")
    # st.sidebar.subheader("📺 Learn Data Science")
    # st.sidebar.video("https://youtu.be/omk5b1m2h38")
    # st.sidebar.markdown("---")
    # st.sidebar.markdown("Created by: [Dr. Muhammad Aammar Tufail](https://github.com/AammarTufail)")
    # st.sidebar.markdown("Contact: [Email](mailto:aammar@codanics.com)")
