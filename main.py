from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import os

# === App setup ===
app = Flask(__name__, static_folder='static')
CORS(app)

# === Serve the main index.html ===
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# === Serve static files (CSS, JS, images) ===
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# === Consultation API endpoint ===
@app.route('/api/consult', methods=['POST'])
def consult():
    data = request.get_json()
    symptoms = data.get('symptoms', [])
    duration = data.get('duration')
    severity = data.get('severity')
    notes = data.get('notes', '')

    # Diagnosis logic
    diagnosis, treatment, lab_exams = generate_diagnosis(symptoms)

    report = {
        "symptoms": symptoms,
        "duration": duration,
        "severity": severity,
        "notes": notes,
        "diagnosis": diagnosis,
        "treatment": treatment,
        "labExams": lab_exams
    }

    return jsonify(report), 201

# === Rule-based diagnosis logic ===
def generate_diagnosis(symptoms):
    s = [sym.lower() for sym in symptoms]

    rules = [
        (lambda s: 'fever' in s and 'cough' in s,
         'Likely upper respiratory tract infection (URTI)',
         'Paracetamol, rest, fluids',
         'CBC, COVID-19 test'),

        (lambda s: 'toothache' in s,
         'Dental infection',
         'Amoxicillin, Diclofenac, dental referral',
         'Panoramic X-ray'),

        (lambda s: 'diarrhea' in s,
         'Gastroenteritis',
         'Oral rehydration salts, zinc, Metronidazole',
         'Stool analysis, culture'),

        (lambda s: 'headache' in s,
         'Tension headache or migraine',
         'Paracetamol or Ibuprofen, hydration, rest',
         'Blood pressure check, optional CT if persistent')
    ]

    for condition, diag, treat, labs in rules:
        if condition(s):
            return diag, treat, labs

    return 'Unspecified condition', 'Supportive care', 'CBC, Urinalysis'

# === App entry point ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
