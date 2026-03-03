import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from docx import Document
import os
import re
import tempfile
# SPEED HACK 1: ProcessPool ki jagah ThreadPool use kiya hai
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Fast PDF to Word", page_icon="⚡")
st.title("⚡ Fast Scanned PDF Converter")
st.write("Apni PDF upload karein. Yeh app Hindi/English text tezi se extract karega bina extra spaces ke.")

def remove_extra_spaces_and_clean(text):
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned.strip()

def process_single_page(img_path):
    custom_config = r'--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(img_path, lang='eng+hin', config=custom_config)
    return remove_extra_spaces_and_clean(raw_text)

uploaded_file = st.file_uploader("Apni PDF file yahan drag & drop karein", type=["pdf"])

if uploaded_file is not None:
    st.info("File upload ho gayi hai. Conversion shuru karne ke liye niche button dabayein.")
    
    if st.button("Start Fast Conversion 🚀"):
        with st.spinner("⚡ Processing bohot tezi se chal rahi hai... Kripya pratiksha karein"):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(uploaded_file.read())
                    pdf_path = temp_pdf.name
                
                word_path = pdf_path.replace('.pdf', '.docx')
                doc = Document()
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    st.write("Images extract ki ja rahi hain...")
                    
                    # SPEED HACK 2: DPI 200 se 150 kar diya gaya hai (Speed double ho jayegi)
                    image_paths = convert_from_path(
                        pdf_path, dpi=150, output_folder=temp_dir, paths_only=True, fmt='jpeg', grayscale=True
                    )
                    
                    total_pages = len(image_paths)
                    st.write(f"Total {total_pages} pages mile. Fast OCR chal raha hai...")
                    progress_bar = st.progress(0)
                    
                    # SPEED HACK 3: max_workers=4 lagaya hai taaki Cloud server overload na ho
                    with ThreadPoolExecutor(max_workers=4) as executor:
                        extracted_texts = list(executor.map(process_single_page, image_paths))
                    
                    for i, text in enumerate(extracted_texts):
                        if text.strip(): # Khali page hone par kuch na likhe
                            doc.add_paragraph(text)
                            doc.add_paragraph("") 
                        progress_bar.progress((i + 1) / total_pages)
                        
                doc.save(word_path)
                st.success("✅ Fast Conversion poora ho gaya!")
                
                with open(word_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Word File",
                        data=file,
                        file_name=uploaded_file.name.replace('.pdf', '_Fast_Converted.docx'),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
            except Exception as e:
                st.error(f"Ek error aa gaya: {e}")


