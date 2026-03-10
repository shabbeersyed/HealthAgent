🩺 HealthAgent – AI Medical Documentation Assistant

HealthAgent is an AI-powered clinical documentation tool that converts doctor–patient conversations into structured SOAP medical notes automatically.

The system records conversations, converts speech to text, analyzes the discussion using Large Language Models (LLMs), and generates professional medical summaries and reports.

This helps healthcare professionals reduce documentation time, improve accuracy, and focus more on patient care.

⭐ Why This Project?

Doctors often spend a significant amount of time documenting consultations instead of focusing on patients.

Typical challenges include:

• Writing SOAP notes manually
• Transcribing long conversations
• Summarizing medical discussions
• Preparing structured documentation
• Generating consultation reports

HealthAgent automates this entire workflow using AI and natural language processing.

✨ Key Features

✔️ Voice Recording for Consultations
Record doctor–patient conversations directly in the system.

✔️ Speech-to-Text Transcription
Automatically converts audio conversations into text using AI.

✔️ SOAP Note Generator
Creates structured clinical documentation including:

• Subjective
• Objective
• Assessment
• Plan

✔️ AI-Powered Medical Summarization
Uses LLMs to extract medical insights and generate structured summaries.

✔️ PDF Medical Report Generator
Automatically generates downloadable medical consultation reports.

✔️ Email Report Delivery
Sends consultation reports directly to doctors or patients.

🏗️ System Architecture (Simple View)

Doctor–Patient Conversation
⬇
Audio Recording
⬇
Speech-to-Text Conversion
⬇
LLM-Based Medical Analysis
⬇
SOAP Note Generation
⬇
PDF Report Creation
⬇
Optional Email Delivery

🛠️ Tech Stack
Backend

Python
Flask

AI / NLP

OpenAI API
Large Language Models (LLMs)
Prompt Engineering
Speech Recognition

Frontend

React
Vite

Document Processing

ReportLab (PDF generation)

Other Tools

SMTP Email Integration
JSON Data Processing
Git Version Control

📁 Project Structure
HealthAgent/
│
├── backend/
│   ├── app.py
│   ├── speech_processing.py
│   ├── summarizer.py
│   ├── report_generator.py
│
├── frontend/
│   ├── src/
│   ├── components/
│
├── requirements.txt
│
└── README.md
⚙️ How to Run Locally (Beginner Friendly)
1️⃣ Clone the repository
git clone https://github.com/shabbeersyed/HealthAgent
2️⃣ Navigate to the project
cd HealthAgent
3️⃣ Install backend dependencies
pip install -r requirements.txt
4️⃣ Run the backend server
python app.py
5️⃣ Start the frontend
npm install
npm run dev
📡 Example Workflow

1️⃣ Doctor records a conversation with a patient

2️⃣ HealthAgent converts the audio into text

3️⃣ The system processes the conversation using an LLM

4️⃣ The AI extracts medical insights and generates SOAP notes

5️⃣ A professional PDF medical report is created

6️⃣ The report can be downloaded or emailed

🚀 Future Improvements

• Real-time transcription during consultations
• Integration with Electronic Health Record (EHR) systems
• Secure patient data storage
• Fine-tuned medical LLMs
• Mobile-friendly interface for doctors

❤️ Made By

Shabbeer Basha Syed
AI & Automation Engineer
MS Information Systems & Technology
University of North Texas

Video: https://www.linkedin.com/posts/shabbeer-basha-syed_healthagent-hack4health-hackwell2025-activity-7389870640486572032-PLr-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFImeawBe0c1XOuRN4MzMNBEHI8K_-m3_yM
