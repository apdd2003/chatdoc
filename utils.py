import os
from flask import session
from langchain.chat_models import ChatOpenAI # used for GPT3.5/4 model
# from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from apikey import apikey

os.environ["OPENAI_API_KEY"] = apikey

def chunk_embed(file_name, np):
    with open(f'uploads/{file_name}','rb') as f:
        bytes_data = f.read()
    with open (file_name, 'wb') as f:
        
        f.write(bytes_data)
        name, extension = os.path.splitext(file_name)
        if extension == '.pdf':
            from langchain.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_name)
        elif extension == '.docx':
            from langchain.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_name)
        elif extension == '.txt':
            from langchain.document_loaders import TextLoader
            loader = TextLoader(file_name)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_documents(chunks, embeddings, collection_name=np)
        # initialize OpenAI instance
        llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
        retriever=vector_store.as_retriever()
        crc = ConversationalRetrievalChain.from_llm(llm, retriever)
        return crc

def askdoc(question, crc):
    if question:
        response = crc.run({
                'question': question,
                'chat_history': session['history']
            })
        return response
            