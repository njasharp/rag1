import os
import pdfplumber
import streamlit as st
from groq import Groq
from gtts import gTTS

# Ensure the API key is set
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY environment variable not set. Please set it and restart the application.")
    raise ValueError("GROQ_API_KEY environment variable not set")

# Initialize the Groq client
try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    raise

# Function to generate and play text-to-speech audio
def generate_audio(audio_text, filename="audio.mp3"):
    try:
        tts = gTTS(text=audio_text, lang='en')
        tts.save(filename)
        return filename
    except Exception as e:
        st.sidebar.error(f"Failed to generate text-to-speech: {e}")
        return None

st.image("ai.PNG", width=120)
st.title("Welcome to GChat with rag Plus audio AI")

# Sidebar
st.sidebar.title("Query Box")

# System prompt input in the sidebar
system_prompt = st.sidebar.text_area("Enter system prompt (optional):", value="", height=100)

# User prompt input in the sidebar
prompt = st.sidebar.text_area("Enter your prompt:", value="", height=150)

# Short-term memory input in the sidebar
short_term_memory = st.sidebar.text_area("Enter short-term memory (optional):", value="", height=100)

# File upload input in the sidebar
uploaded_file = st.sidebar.file_uploader("Upload a text or PDF file", type=["txt", "pdf"])

# Function to read the contents of the uploaded text file
def read_uploaded_text(file):
    return file.read().decode("utf-8")

# Function to read the contents of the uploaded PDF file
def read_uploaded_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Read the content of the uploaded file, if any
file_content = ""
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        file_content = read_uploaded_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        file_content = read_uploaded_text(uploaded_file)

# Function to query Groq API
def query_groq(system_prompt, combined_prompt):
    try:
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })
        messages.append({
            "role": "user",
            "content": combined_prompt,
        })

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Initialize session state variables
if 'analysis_result_text' not in st.session_state:
    st.session_state.analysis_result_text = ""

# Display the analysis result
analysis_result = st.empty()
if st.session_state.analysis_result_text:
    analysis_result.write(f"Analysis Result: {st.session_state.analysis_result_text}")

# Button to submit the query
if st.sidebar.button("Submit"):
    if prompt or file_content:
        with st.spinner("Querying the chatbot..."):
            # Combine short-term memory, file content, and user prompt
            combined_prompt = f"{short_term_memory}\n{file_content}\n{prompt}"
            # Query Groq's API
            reply = query_groq(system_prompt, combined_prompt)
            if reply:
                st.session_state.analysis_result_text = reply  # Store the result in the session state
                st.success("Query completed!")
                analysis_result.write(f"Analysis Result: {reply}")
            else:
                st.error("No response found.")
    else:
        st.sidebar.warning("Please enter a prompt or upload a file.")

# Sidebar button to speak the analysis result
if st.sidebar.button("Speak Analysis Result"):
    audio_file = generate_audio(st.session_state.analysis_result_text)
    if audio_file:
        st.audio(audio_file)

# Reset button
if st.sidebar.button("Reset"):
    st.session_state.analysis_result_text = ""  # Clear the analysis result
    st.experimental_rerun()

# Instructions
st.write("Enter a system prompt (optional), a short-term memory (optional), and a user prompt in the sidebar, then click 'Submit' to get a response from the LLM.")
st.write("Alternatively, you can upload a text or PDF file to use its content as the prompt.")
st.write("Model: llama3-8b-8192")
st.info('build by DW v3') #v7rec

# Text input for user name
talk1 = st.text_input("Enter your text:")

# Button to trigger speaking the text input
if st.button("Speak!"):
    if talk1:
        st.write("Speaking...")
        audio_file = generate_audio(talk1)
        if audio_file:
            st.audio(audio_file)