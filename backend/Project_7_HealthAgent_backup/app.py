# --- Version 5: Flask + Dynamic Patient Info + SOAP JSON PDF + Email Sending ---
import os
import uuid
import json
import smtplib
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# === OpenAI setup ===
client = OpenAI(api_key="OPENAI_API_KEY")

# === Directories ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS = os.path.join(BASE_DIR, "Recordings")
SOAP_FOLDER = os.path.join(BASE_DIR, "SOAP")
os.makedirs(RECORDINGS, exist_ok=True)
os.makedirs(SOAP_FOLDER, exist_ok=True)

samplerate = 44100
recording_data = []
stream = None

# === Recording ===
def callback(indata, frames, time, status):
    recording_data.append(indata.copy())

def start_recording_internal():
    global stream, recording_data
    print("🎙️ Recording started...")
    recording_data = []
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="int16", callback=callback)
    stream.start()

def stop_recording_internal():
    global stream, recording_data
    if stream:
        stream.stop()
        stream.close()
    print("⏹️ Recording stopped.")
    if not recording_data:
        raise ValueError("No audio recorded.")
    wav_path = os.path.join(RECORDINGS, f"recording_{uuid.uuid4().hex}.wav")
    audio = np.concatenate(recording_data, axis=0)
    write(wav_path, samplerate, audio)
    print(f"✅ Saved audio to {wav_path}")
    return wav_path

# === PDF creation ===
def create_pdf(summary_text, patient_data, pdf_path):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"],
                                 fontSize=20, textColor=colors.HexColor("#004080"), alignment=1)
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"],
                                   fontSize=14, textColor=colors.HexColor("#800000"), spaceAfter=10)
    normal_style = ParagraphStyle("NormalStyle", parent=styles["Normal"], fontSize=11, leading=14)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    elements.append(Paragraph("🏥 HEALTHCARE CONSULTATION REPORT", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("👤 Patient Information", section_style))
    for key, label in [
        ("name", "Name"),
        ("age", "Age"),
        ("weight", "Weight (kg)"),
        ("email", "Email"),
        ("reason", "Reason for Visit"),
    ]:
        val = patient_data.get(key, "N/A")
        elements.append(Paragraph(f"<b>{label}:</b> {val}", normal_style))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("🩺 SOAP Summary", section_style))

    try:
        clean = summary_text.strip().replace("```", "").replace("json", "").strip()
        parsed = json.loads(clean)
        soap_data = parsed.get("SOAP", parsed)
        for sec, val in soap_data.items():
            elements.append(Paragraph(f"<b>{sec}:</b>", section_style))
            if isinstance(val, str):
                elements.append(Paragraph(val, normal_style))
            elif isinstance(val, dict):
                for k, v in val.items():
                    elements.append(Paragraph(f"• <b>{k}:</b> {v}", normal_style))
            elif isinstance(val, list):
                for item in val:
                    elements.append(Paragraph(f"• {item}", normal_style))
            elements.append(Spacer(1, 0.1 * inch))
    except Exception as e:
        print("⚠️ JSON parse failed:", e)
        elements.append(Paragraph(summary_text, normal_style))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("<i>End of Report — Generated Automatically</i>", normal_style))
    doc.build(elements)
    print(f"📄 PDF generated successfully at: {pdf_path}")

# === Routes ===
@app.route("/start_recording", methods=["POST"])
def start_recording_route():
    try:
        start_recording_internal()
        return jsonify({"success": True, "message": "Recording started"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/stop_recording", methods=["POST"])
def stop_recording_route():
    try:
        patient_data = request.get_json() or {}
        print("📋 Patient data received:", patient_data)
        wav_path = stop_recording_internal()

        # Transcribe
        with open(wav_path, "rb") as f:
            transcript = client.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=f)
        text = transcript.text
        print("✅ Transcription complete.")

        # SOAP Summary
        prompt = f"""
        Summarize this conversation into SOAP (Subjective, Objective, Assessment, Plan).
        Return JSON only.
        Conversation:
        {text}
        """
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": "You are a medical documentation assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        summary = response.choices[0].message.content.strip()

        # PDF
        pdf_filename = f"SOAP_Report_{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(SOAP_FOLDER, pdf_filename)
        create_pdf(summary, patient_data, pdf_path)

        return jsonify({"success": True, "summary": summary, "pdf_path": f"SOAP/{pdf_filename}"})
    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/SOAP/<path:filename>")
def serve_soap_file(filename):
    return send_from_directory(SOAP_FOLDER, filename)

# === New Route: Send Email ===
@app.route("/send_email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()
        recipient_email = data.get("email")
        patient_name = data.get("name", "Patient")
        summary = data.get("summary", "")
        tests = data.get("tests", [])

        if not recipient_email:
            return jsonify({"success": False, "error": "Missing recipient email"}), 400

        # Compose Email
        subject = f"Consultation Summary for {patient_name}"
        body = f"""
Dear {patient_name},

Here’s your consultation summary:

🩺 Summary:
{summary}

🧪 Tests to Order:
{', '.join(tests) if tests else 'No tests ordered'}

Thank you for using Health Agent.
Stay healthy,
— Health Agent AI System
"""

        msg = MIMEMultipart()
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # ✅ Gmail SMTP setup
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            msg["From"] = "healthagentbot@gmail.com"
            server.login(os.environ.get("EMAIL_USER"), os.environ.get("EMAIL_PASS"))  # <-- app password, no spaces
            server.send_message(msg)

        print(f"✅ Email sent to {recipient_email}")
        return jsonify({"success": True, "message": f"Email sent to {recipient_email}"})

    except Exception as e:
        print("❌ Email send error:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# === Run Flask ===
if __name__ == "__main__":
    print("🚀 Flask server running at http://127.0.0.1:5000")
    app.run(debug=True)
