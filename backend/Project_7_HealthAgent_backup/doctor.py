# --- Version 1 ----
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from openai import OpenAI
import os
from datetime import datetime
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors

client = OpenAI(api_key="OPENAI_API_KEY")

# Folders
os.makedirs("Recordings", exist_ok=True)
os.makedirs("SOAP", exist_ok=True)

samplerate = 44100
recording_data = []
stream = None
unique_id = str(uuid.uuid4())

def start_recording():
    """Call this when 'Start Recording' button is clicked"""
    global stream, recording_data
    print("🔴 Recording started...")
    recording_data = []
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='int16', callback=callback)
    stream.start()

def callback(indata, frames, time, status):
    """Collects chunks of live audio"""
    recording_data.append(indata.copy())

def stop_recording():
    """Call this when 'Stop Recording' button is clicked"""
    global stream, recording_data
    if stream:
        stream.stop()
        stream.close()
    print("⏹️ Recording stopped.")

    # Save audio
    wav_path = os.path.join("Recordings", f"recording_{unique_id}.wav")
    audio = np.concatenate(recording_data, axis=0)
    write(wav_path, samplerate, audio)
    print(f"✅ Saved voice as '{wav_path}'")

    # --- Transcribe ---
    with open(wav_path, "rb") as f:
        print("Transcribing and summarizing with LLM...")
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f
        )

    text = transcript.text
    print(f"\n Raw transcription:\n{text}\n")

    # --- SOAP Summary ---
    prompt = f"""
    Rephrase and summarize perfectly in SOAP format (Subjective, Objective, Assessment, Plan):
    DONT MISS TO CAPTURE ALL INFORMATION FROM PATIENT, INCLUDING NAME, BIOGRPAHICAL INFORMATION.
    Please always store this information in json format.
    DONT MISS TESTS, LABS, REPORTS, ACTIVITIES, MEDICINES SUGGESTED BY DOCTOR.
    -----
    {text}
    -----
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a medical documentation assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response.choices[0].message.content.strip()  # type: ignore

    # ✅ Fetch patient info inside this function to avoid NameError
    patient_data = get_patient_info()

    # ✅ Replace “Not provided” with actual info
    summary = summary.replace('"name": "Not provided"', f'"name": "{patient_data["name"]}"')
    summary = summary.replace('"age": "Not provided"', f'"age": "{patient_data["age"]}"')
    summary = summary.replace('"gender": "Not provided"', f'"gender": "{patient_data["gender"]}"')
    summary = summary.replace('"address": "Not provided"', '"address": "NA"')
    summary = summary.replace('"contact_number": "Not provided"', '"contact_number": "NA"')

    print("\n SOAP Summary:\n")
    print(summary)

    soap_path = os.path.join("SOAP", f"soap_summary_{unique_id}.txt")
    with open(soap_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"\n Saved SOAP summary to '{soap_path}'")

    return {"audio_file": wav_path, "soap_file": soap_path, "summary": summary}


import json

# ✅ 1. Load patient info automatically (no input)
# ✅ 1. Load patient info automatically (from in-code values, not file)
def get_patient_info():
    """Return patient details already embedded in the code — no external file"""
    # Pre-filled values; edit here if needed
    data = {
        "name": "Shabbir",
        "age": "24",
        "gender": "Male",
        "height": "175 cm",
        "weight": "70 kg",
        "blood_pressure": "120/80 mmHg",
        "temperature": "98.6°F",
        "allergies": "None",
        "diagnosis": "To Be Checked",
        "doctor_name": "Dr. John Smith"
    }
    print(f"🩺 Loaded patient details for {data['name']} (pre-filled in code)")
    return data



# ✅ 2. Make PDF more beautiful & readable (human-friendly summary)
def create_pdf(summary_text, patient_data, pdf_path):
    """Generate a visually enhanced, patient-friendly PDF report"""
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#004080"),
        spaceAfter=14,
        alignment=1  # center
    )
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#800000"),
        spaceAfter=10,
        underlineWidth=1
    )
    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
    )

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []

    # Header
    elements.append(Paragraph("🏥 HEALTHCARE CONSULTATION REPORT", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("<b>Date:</b> " + datetime.now().strftime("%B %d, %Y"), normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Patient Info Section
    elements.append(Paragraph("👤 Patient Information", section_style))
    for key, value in patient_data.items():
        elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Try to prettify SOAP summary
    elements.append(Paragraph("🩺 SOAP Summary", section_style))
    try:
        # clean code block wrappers (```json ... ```)
        clean = summary_text.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[-2] if "```" in clean else clean
        if clean.lower().startswith("json"):
            clean = clean[4:].strip()
        clean = clean.replace("```", "").strip()

        parsed = json.loads(clean)
        # merge doctor’s embedded data to override missing fields
# --- Merge doctor info to fill missing patient fields for consistency ---
        for k, v in patient_data.items():
            if (
                k not in parsed.get("patient", {}) or
                not parsed["patient"][k] or
                parsed["patient"][k] in ["", None, "Not provided"]
            ):
                parsed.setdefault("patient", {})[k] = v

        # remove redundant biographical_information if all values are None
        bio_info = parsed["patient"].get("biographical_information", {})
        if isinstance(bio_info, dict) and all(v in [None, "", "Not provided"] for v in bio_info.values()):
            parsed["patient"].pop("biographical_information", None)



        # --- Reformat parsed JSON into nice readable sections ---

        elements.append(Paragraph("<b>SOAP Breakdown</b>", section_style))
        soap = parsed.get("SOAP", {})
        for sec, val in soap.items():
            elements.append(Spacer(1, 0.05 * inch))
            elements.append(Paragraph(f"<b>{sec}:</b>", section_style))

            if isinstance(val, dict):
                # dict → bullet lines; handle nested lists/dicts nicely
                for sub, sv in val.items():
                    if isinstance(sv, list):
                        elements.append(Paragraph(f" • <b>{sub.replace('_', ' ').title()}:</b>", normal_style))
                        for item in sv:
                            if isinstance(item, dict):
                                # list of dicts → inline key:value pairs
                                kv = ", ".join(
                                    [f"<b>{k.replace('_', ' ').title()}:</b> {v}" for k, v in item.items()]
                                )
                                elements.append(Paragraph(f"  • {kv}", normal_style))
                            else:
                                elements.append(Paragraph(f"  • {item}", normal_style))
                    elif isinstance(sv, dict):
                        elements.append(Paragraph(f" • <b>{sub.replace('_', ' ').title()}:</b>", normal_style))
                        for k2, v2 in sv.items():
                            elements.append(Paragraph(f"  • <b>{k2.replace('_', ' ').title()}:</b> {v2}", normal_style))
                    else:
                        elements.append(Paragraph(f" • <b>{sub.replace('_', ' ').title()}:</b> {sv}", normal_style))

            elif isinstance(val, list):
                # top-level list → bullets
                for item in val:
                    if isinstance(item, dict):
                        kv = ", ".join(
                            [f"<b>{k.replace('_', ' ').title()}:</b> {v}" for k, v in item.items()]
                        )
                        elements.append(Paragraph(f" • {kv}", normal_style))
                    else:
                        elements.append(Paragraph(f" • {item}", normal_style))
            else:
                # plain string/number → just print
                pretty_val = str(val).strip()
                elements.append(Paragraph(pretty_val, normal_style))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("<i>End of Report — Generated Automatically</i>", normal_style))

    except Exception as e:
        print("⚠️ JSON parse failed, fallback:", e)
        pretty_text = summary_text.replace("\n", "<br/>").replace("{", "").replace("}", "")
        elements.append(Paragraph(pretty_text, normal_style))

    # Build PDF safely
    doc.build(elements)
    print(f"📄 PDF generated successfully at: {pdf_path}")



# ✅ 3. Main block (unchanged logic, only replaced patient input)
if __name__ == "__main__":
    print("🎙️ Type 'start' to begin and 'stop' to end recording.")
    cmd = input("👉 Enter command: ").strip().lower()

    if cmd == "start":
        start_recording()
        input(" Recording... Press Enter to stop.")  # Wait manually
        result = stop_recording()
        print("\n Summary Saved:")
        print(result["summary"])

        # Load details from JSON and create a visually rich PDF
        patient_data = get_patient_info()
        pdf_path = os.path.join("SOAP", f"SOAP_Report_{unique_id}.pdf")
        create_pdf(result["summary"], patient_data, pdf_path)
