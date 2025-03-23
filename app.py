from dotenv import load_dotenv

load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import fitz  # PyMuPDF
import google.generativeai as genai
import sys
import platform

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def check_poppler_installation():
    try:
        if platform.system() == "Windows":
            # Check if Poppler is in PATH
            from shutil import which
            if which("pdftoppm") is None:
                st.error("""
                Poppler is not installed or not in PATH. Please follow these steps:
                1. Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/
                2. Extract the zip file
                3. Copy the extracted folder to C:\\Program Files
                4. Add the bin folder (e.g., C:\\Program Files\\poppler-24.02.0\\Library\\bin) to your system PATH
                5. Restart your computer
                """)
                return False
        return True
    except Exception as e:
        st.error(f"Error checking Poppler installation: {str(e)}")
        return False

def get_gemini_response(input, pdf_content, prompt):
    """Get response from Gemini model using text content."""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        # Combine the text content with the prompt
        combined_prompt = f"{input}\n\nResume Content:\n{pdf_content}\n\nJob Description:\n{prompt}"
        response = model.generate_content(combined_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return "Sorry, there was an error processing your request. Please try again."

def input_pdf_setup(uploaded_file):
    """Process uploaded PDF file and return its content."""
    try:
        # Save the uploaded file temporarily
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # First try to read text content using PyMuPDF
        doc = fitz.open("temp.pdf")
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        doc.close()
        
        # Now try to get the first page as image using pdf2image
        try:
            from pdf2image import convert_from_path
            images = convert_from_path("temp.pdf", first_page=1, last_page=1, dpi=300)
            if images:
                img = images[0]
                img.save("temp.jpg", "JPEG")
            else:
                st.warning("Could not extract image from PDF, but text content was successfully extracted.")
                img = None
        except Exception as img_error:
            st.warning("Could not extract image from PDF, but text content was successfully extracted.")
            img = None
        
        # Clean up
        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")
        
        return text_content, img
        
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        # Clean up any temporary files
        for temp_file in ["temp.pdf", "temp.jpg"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        return None, None

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Check Poppler installation at startup
if not check_poppler_installation():
    st.warning("Please install Poppler to process PDF files.")

input_text=st.text_area("Job Description: ",key="input")
uploaded_file=st.file_uploader("Upload your resume(PDF)...",type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")

#submit2 = st.button("How Can I Improvise my Skills")

submit3 = st.button("Percentage match")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        with st.spinner("Processing your resume..."):
            text_content, img = input_pdf_setup(uploaded_file)
            if text_content:
                response = get_gemini_response(input_prompt1, text_content, input_text)
                st.subheader("The Response is")
                st.write(response)
    else:
        st.write("Please upload the resume")

elif submit3:
    if uploaded_file is not None:
        with st.spinner("Analyzing your resume..."):
            text_content, img = input_pdf_setup(uploaded_file)
            if text_content:
                response = get_gemini_response(input_prompt3, text_content, input_text)
                st.subheader("The Response is")
                st.write(response)
    else:
        st.write("Please upload the resume")



   




