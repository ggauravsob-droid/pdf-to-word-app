import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from docx import Document
import os
import re
import tempfile
import time # Timer ke liye

st.set_page_config(page_title="Stable PDF Converter", page_icon="📄")
st.title("📄 Scanned PDF Converter (Stable Mode)")
st.write("Apni PDF upload karein. Yeh app Hindi/English text extract karega aur aapko Live Status dikhayega.")

def remove_extra_spaces_and_clean(text):
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    cleaned = re.sub(r' {2,}', ' ', cleaned)
    return cleaned.strip()

uploaded_file = st.file_uploader("Apni PDF file yahan drag & drop karein", type=["pdf"])

if uploaded_file is not None:
    if st.button("Start Conversion 🚀"):
        with st.spinner("Processing shuru ho rahi hai..."):
            try:
                start_time = time.time()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf.write(uploaded_file.read())
                    pdf_path = temp_pdf.name
                
                word_path = pdf_path.replace('.pdf', '.docx')
                doc = Document()
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    st.info("1. PDF se images banayi ja rahi hain... (Please wait)")
                    
                    # 150 DPI is best for Speed vs Quality balance
                    image_paths = convert_from_path(
                        pdf_path, dpi=150, output_folder=temp_dir, paths_only=True, fmt='jpeg', grayscale=True
                    )
                    
                    total_pages = len(image_paths)
                    st.success(f"✅ Total {total_pages} pages mil gaye.")
                    
                    st.write("---")
                    st.write("### ⚙️ Live Processing Status")
                    
                    # LIVE TRACKING WIDGETS
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    timer_text = st.empty()
                    
                    # EK-EK KARKE PAGE PADHNA (TAAKI SERVER CRASH NA HO)
                    for i, img_path in enumerate(image_paths):
                        # Timer Update karna
                        elapsed = int(time.time() - start_time)
                        timer_text.info(f"⏱️ **Time Elapsed:** {elapsed} seconds")
                        
                        # Screen par batana ki konsa page padh raha hai
                        status_text.warning(f"⏳ **Reading Page {i+1} of {total_pages}**... OCR chal raha hai.")
                        
                        # Text nikalna
                        custom_config = r'--oem 3 --psm 6'
                        raw_text = pytesseract.image_to_string(img_path, lang='eng+hin', config=custom_config)
                        cleaned_text = remove_extra_spaces_and_clean(raw_text)
                        
                        # Word mein likhna
                        if cleaned_text:
                            doc.add_paragraph(cleaned_text)
                            doc.add_paragraph("") 
                            
                        # Progress bar update
                        progress_bar.progress((i + 1) / total_pages)
                        status_text.success(f"✅ **Page {i+1} done!**")
                        
                # FINAL SAVE
                doc.save(word_path)
                total_time = int(time.time() - start_time)
                
                st.write("---")
                st.success(f"🎉 **Conversion poora ho gaya!** Total samay laga: {total_time} seconds.")
                
                with open(word_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Word File",
                        data=file,
                        file_name=uploaded_file.name.replace('.pdf', '_Converted.docx'),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
            except Exception as e:
                st.error(f"❌ Ek error aa gaya: {e}")



