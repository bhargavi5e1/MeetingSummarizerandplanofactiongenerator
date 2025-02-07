import streamlit as st
import os
import base64
import tempfile
import moviepy.editor as mp
import speech_recognition as sr
from textblob import TextBlob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai

# Set your OpenAI API key
openai.api_key = 'your_key'  # Replace with your actual OpenAI API key

# Path to background image
background_image_path = "C:\\Users\\Bhargavi\\OneDrive\\Desktop\\7971.jpg"  # Update with your image path

# Function to encode image to base64
def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

base64_background = get_base64_of_bin_file(background_image_path)

# Custom CSS styling
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_background}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .stButton > button {{
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }}
    h1, h2, h3, p, label {{
        color: white;
    }}
    textarea {{
        color: white;
        background-color: rgba(0, 0, 0, 0.5);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Function for summarization using OpenAI API
def summarize_text_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n{text}"}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

# Function for generating a Plan of Action using OpenAI API
def generate_plan_of_action_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate a plan of action based on the following meeting transcription:\n{text}"}
        ],
        max_tokens=200
    )
    return response['choices'][0]['message']['content'].strip()

# Functions for audio/video processing
def extract_audio(video_path, output_audio_path):
    with mp.VideoFileClip(video_path) as video:
        video.audio.write_audiofile(output_audio_path)

def audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)

def analyze_sentiments(transcription):
    analysis = TextBlob(transcription)
    sentiment = "Positive" if analysis.sentiment.polarity > 0 else "Negative" if analysis.sentiment.polarity < 0 else "Neutral"
    return sentiment

def detect_meeting_genre(transcription):
    keywords = {
        "business": "Business",
        "technical": "Technical",
        "team": "Team Meeting",
        "brainstorming": "Brainstorming",
        "planning": "Planning",
        "casual": "Casual",
        "class": "Classroom Meeting",
        "meeting": "Meeting",
        "employee": "Meeting",
        "manager": "Meeting"
    }
    for keyword, genre in keywords.items():
        if keyword in transcription.lower():
            return genre
    return "Uncategorized"

def estimate_speaker_count(segments, threshold=1):
    speaker_changes = 1
    previous_end = segments[0]["end"]
    for segment in segments[1:]:
        start = segment["start"]
        if (start - previous_end) < threshold:
            speaker_changes += 1
        previous_end = segment["end"]
    return speaker_changes

# Email functionality
def send_mail(sender_email, recipient_email, subject, body, sender_password):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "html"))
            server.sendmail(sender_email, recipient_email, message.as_string())
            return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Streamlit app
st.title("Meeting Summarizer and Action Plan Generator")

uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "wav", "mp4", "mkv"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        uploaded_file_path = temp_file.name

    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name

    if st.button("Process"):
        try:
            if file_extension in ["mp4", "mkv"]:
                extract_audio(uploaded_file_path, audio_path)
            else:
                audio_path = uploaded_file_path

            transcription = audio_to_text(audio_path)
            summary = summarize_text_openai(transcription)
            plan_of_action = generate_plan_of_action_openai(transcription)
            sentiment = analyze_sentiments(transcription)
            genre = detect_meeting_genre(transcription)

            segments = [
                {"start": 0, "end": 5},
                {"start": 5, "end": 12},
            ]
            speakers = estimate_speaker_count(segments)

            st.session_state.results = {
                "summary": summary,
                "plan_of_action": plan_of_action,
                "sentiment": sentiment,
                "genre": genre,
                "speaker_count": speakers
            }

            st.subheader("Meeting Summary")
            st.text_area("Summary", summary, height=150)

            st.subheader("Plan of Action")
            st.text_area("Plan of Action", plan_of_action, height=150)

            st.subheader("Overall Sentiment")
            st.write(sentiment)

            st.subheader("Meeting Genre")
            st.write(genre)

            st.subheader("Estimated Number of Speakers")
            st.write(speakers)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Email functionality
st.subheader("Send Summary via Email")
sender_email = st.text_input("Your Email")
sender_password = st.text_input("Your Email Password", type="password")
recipient_email = st.text_input("Recipient Email")

if st.button("Send Email"):
    if "results" in st.session_state:
        results = st.session_state.results
        if results["summary"] and sender_email and recipient_email and sender_password:
            subject = "Meeting Summary and Plan of Action"
            body = f"""
            <h3>Meeting Summary</h3>
            <p>{results['summary']}</p>
            <h3>Plan of Action</h3>
            <p>{results['plan_of_action']}</p>
            <h3>Meeting Genre</h3>
            <p>{results['genre']}</p>
            <h3>Overall Sentiment</h3>
            <p>{results['sentiment']}</p>
            <h3>Estimated Speaker Count</h3>
            <p>{results['speaker_count']}</p>
            """
            if send_mail(sender_email, recipient_email, subject, body, sender_password):
                st.success(f"Email sent successfully to {recipient_email}")
            else:
                st.error("Failed to send email. Check your email credentials.")
        else:
            st.error("Please process the file and ensure sender/recipient email addresses are provided.")
    else:
        st.error("Please process the file first.")
