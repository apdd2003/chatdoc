from flask import Flask, render_template, redirect, url_for, flash, request, current_app, make_response, session, jsonify, json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import os
from utils import chunk_embed, askdoc
import uuid
from dotenv import load_dotenv
load_dotenv()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth = HTTPBasicAuth()
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)



users = {
    'shaikh': generate_password_hash(os.getenv('password')),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username
    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['GET', 'POST'])
@auth.login_required
@limiter.limit("20/day", override_defaults=False)
def home():
    session['uid'] = str(uuid.uuid4())
    query = request.args.get('query')
    if request.method == 'POST':
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['file_name'] = filename
            session['history'] = []
            return render_template("home.html", filename=filename)
        
    return render_template("home.html")

@app.route('/chat')
@limiter.limit("10/day")
def chat():
    query = request.args.get('query')
    file_name  = session['file_name'] 
    print(file_name)
    nspace = session['uid']
    crc = chunk_embed(file_name, nspace)
    answer = askdoc(query,crc)
    session['query'] = query
    session['answer'] = answer
    session['history'].append((query, answer))
    print(answer)

    return redirect(url_for('home'))


@app.route('/redact', methods=['GET','POST'])
@limiter.exempt
def redact():
    from anonymize import redaction
    query = request.form.get('query2')
    print(query)
    if request.method == 'POST':
        res = redaction(query)
        return render_template('anonymize.html', redacted_text=res)

    return render_template("anonymize.html")


@app.route('/entities', methods=['GET','POST'])
@limiter.exempt
def entities():
    # Load BioBERT model and tokenizer
    model_name = "d4data/biomedical-ner-all"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name)

    # Create a NER pipeline
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    query = request.form.get('query2')
    print(query)
    if request.method == 'POST':
        
        # Define a sample clinical text
        # text = """
        # The patient is a 65-year-old male with a history of hypertension and diabetes mellitus,
        # who presented with chest pain radiating to the left arm. ECG showed ST-segment elevation
        # in leads II, III, and aVF. Cardiac enzymes were elevated, and the patient was diagnosed
        # with an acute myocardial infarction. Treatment included aspirin, beta-blockers, and
        # coronary angioplasty. The patient tolerated the procedure well and was transferred
        # to the coronary care unit for further monitoring and management.
        # """

        # Perform NER
        entities = ner_pipeline(query)
        print(type(entities))
        # Print the entities
        print("Named Entities:")
        data = []
        for entity in entities:
            print(entity)
            new_data = {"entity_group":entity['entity_group'], "entity_name":entity['word']}
            data.append(new_data)
        print(data)
        return render_template('ner.html', ner_data=data, query=query)

    return render_template('ner.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)