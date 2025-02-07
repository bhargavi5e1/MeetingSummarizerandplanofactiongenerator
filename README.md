# MeetingSummarizerandplanofactiongenerator

# Brief Summary of The Project
The Meeting Summarizer and Plan of Action Generator is a system designed to process video or audio recordings of meetings, automatically generating a concise summary and actionable plan of action. Using advanced machine learning and speech recognition models, the system analyzes the content of the meeting, identifies the meeting's genre (e.g., business, brainstorming, technical, etc.), and determines the number of speakers involved. 

Key functionalities include:
- Extracting and transcribing speech from video/audio recordings.
- Categorizing the meeting into its respective genre.
- Generating a summary and a plan of action based on the discussed content.
- Sending an automated email to predefined recipients with the summary and action plan attached.
# Technical Stack:
- **Python**: Core programming language for system development.
- **VS Code**: IDE for coding and debugging.
- **Hugging Face**: Utilized for NLP tasks such as text summarization.
- **MoviePy**: Used for video editing and extracting audio from meeting recordings.
- **SpeechRecognition**: Converts spoken language from audio recordings into text.
- **Streamlit**: Enables the creation of user-friendly interfaces for easy interaction.
- **PyAudio**: Captures live audio streams for real-time speech recognition.
- **SMTP Library**: Sends automated emails to recipients with the generated summary and action plan.
