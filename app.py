from flask import Flask, render_template, redirect, url_for, flash, request, current_app, make_response, session
from werkzeug.utils import secure_filename
import os
from utils import chunk_embed, askdoc

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/',methods=['GET', 'POST'])
def home():
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
def chat():
    query = request.args.get('query')
    file_name  = session['file_name'] 
    print(file_name)
    crc = chunk_embed(file_name)
    answer = askdoc(query,crc)
    session['query'] = query
    session['answer'] = answer
    session['history'].append((query, answer))
    print(answer)

    return redirect(url_for('home'))
if __name__ == "__main__":
    app.run(debug=True, port=5000)