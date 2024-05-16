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

# os.environ["OPENAI_API_KEY"] = apikey
# def clear_history():
#     if 'history' in st.session_state:
#         del st.session_state['history']
# st.title('Chat with Document') # title in our web page
# uploaded_file = st.file_uploader('Upload file:',type=['pdf','docx', 'txt'])
# add_file = st.button('Add File', on_click=clear_history)
# if uploaded_file and add_file:
#     with st.spinner('Reading, chunking and embedding file...'):
#         bytes_data = uploaded_file.read()
#         file_name = os.path. join('./', uploaded_file.name)
#         with open (file_name, 'wb') as f:
#             f.write(bytes_data)
#         name, extension = os.path.splitext(file_name)
#         if extension == '.pdf':
#             from langchain.document_loaders import PyPDFLoader
#             loader = PyPDFLoader(file_name)
#         elif extension == '.docx':
#             from langchain.document_loaders import Docx2txtLoader
#             loader = Docx2txtLoader(file_name)
#         elif extension == '.txt':
#             from langchain.document_loaders import TextLoader
#             loader = TextLoader(file_name)
#         else:
#             st.write('Document format is not supported!')

#         # loader = TextLoader(file_name)
#         documents = loader.load()
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = text_splitter.split_documents(documents)
#         embeddings = OpenAIEmbeddings()
#         vector_store = Chroma.from_documents(chunks, embeddings)
#         # initialize OpenAI instance
#         llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
#         retriever=vector_store.as_retriever()
#         crc = ConversationalRetrievalChain.from_llm(llm, retriever)
#         st.session_state.crc = crc
#         # success message when file is chunked & embedded successfully
#         st.success('File uploaded, chunked and embedded successfully')

#     # get question from user input
# question = st.text_input('Input your question')
# if question:
#     if 'crc' in st.session_state:
#         crc = st.session_state.crc
#         if 'history' not in st.session_state:
#             st.session_state['history'] = []
        
#         response = crc.run({
# 'question':question,
# 'chat_history': st.session_state['history']
# })
#         st.session_state['history'].append((question,response))
#         st.write(response)
#         for prompts in st.session_state ['history']:
#             st.write("Question: " + prompts[0])
#             st.write("Answer: " + prompts[1])

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