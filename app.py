import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()  # load all environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Prompt Template
input_prompt = """
Hey, act like a skilled and experienced ATS (Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis, and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider that the job market is very competitive, and you should provide the best assistance for improving the resumes. Assign the percentage match based on JD and highlight the missing keywords with high accuracy.
Resume: {text}
Description: {jd}

I want the response in one single string with the structure:
{{"JD Match":"%","Missing Keywords":[],"Profile Summary":""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS Match")

jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        # Extract text from the PDF
        text = input_pdf_text(uploaded_file)
        
        # Generate response from the model
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))
        
        # Convert response to a dictionary
        response_dict = json.loads(response)
        
        # Prepare data for the table
        data = {
            "JD Match": [response_dict["JD Match"]],
            "Missing Keywords": [", ".join(response_dict["Missing Keywords"])],
            "Profile Summary": [response_dict["Profile Summary"]]
        }

        # Create a DataFrame for tabular display
        df = pd.DataFrame(data)
        
        # Display the response in a table format
        st.subheader("ATS Evaluation Results:")
        st.table(df)
