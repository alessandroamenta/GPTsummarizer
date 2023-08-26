import os
import re
import openai
import requests
from pytube.exceptions import VideoUnavailable
from urllib.parse import urlparse, parse_qs
from moviepy.editor import *
from pytube import YouTube

# Importing custom modules
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Functions for API Key Validation
def validate_openai_key(api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.openai.com/v1/engines", headers=headers)
        response.raise_for_status()
        openai.api_key = api_key
        openai.Completion.create(engine="text-davinci-002", prompt="Hello, World!")
        return True
    except:
        return False

# Functions to Validate YouTube URL
def check_youtube_url_validity(url):
    try:
        yt = YouTube(url)
        if not yt.video_id:
            return False
    except:
        return False
    return yt.streams.filter(adaptive=True).first() is not None

# Function to Get Video Duration
def fetch_video_duration(url):
    yt = YouTube(url)
    return round(yt.length / 60, 2)

# Function to Calculate API Cost
def compute_api_cost(video_length, option):
    cost_factor = 0.009 if option == 'summary' else 0.006
    return round(video_length * cost_factor, 2)

# Function to Fetch Video Metadata
def fetch_video_metadata(url):
    yt = YouTube(url)
    return yt.thumbnail_url, yt.title

# Function to Download Audio from Video
def download_video_audio(url):
    yt = YouTube(url)
    query_params = urlparse(url).query
    parsed_params = parse_qs(query_params)
    video_id = parsed_params["v"][0]
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(output_path="tmp/")
    audio_file_path = os.path.join("tmp/", audio_stream.default_filename)
    audio = AudioFileClip(audio_file_path)
    audio.write_audiofile(os.path.join("tmp/", f"{video_id}.mp3"))
    os.remove(audio_file_path)

# Function to Transcribe Audio
def transcribe_audio_to_text(file_path, video_id):
    transcript_path = f"tmp/{video_id}.txt"
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb < 25:
        with open(file_path, "rb") as audio:
            transcript = openai.Audio.transcribe("whisper-1", audio)
            with open(transcript_path, 'w') as file:
                file.write(transcript['text'])
            os.remove(file_path)
    else:
        print("Audio file size must be under 25 MB.")

# Function to Generate Answer from Transcript
def generate_qa(api_key, url, question):
    # ... (Same as your original code)

# Function to Generate Summary from Transcript
def generate_video_summary(api_key, url):
    # ... (Same as your original code)


# Function to Generate Answer from Transcript
def generate_qa(api_key, url, question):

    openai.api_key = api_key

    llm = OpenAI(temperature=0, openai_api_key=api_key, model_name="gpt-3.5-turbo")
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    # Extract the video_id from the url
    query = urlparse(url).query
    params = parse_qs(query)
    video_id = params["v"][0]

    # The path of the audio file
    audio_path = f"tmp/{video_id}.mp3"

    # The path of the transcript
    transcript_filepath = f"tmp/{video_id}.txt"

    # Check if the transcript file already exist
    if os.path.exists(transcript_filepath):
        
        loader = TextLoader(transcript_filepath, encoding='utf8')
        documents = loader.load()
        
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)

        retriever = db.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        answer = qa.run(question)

    else: 
        download_audio(url)

        # Transcribe the mp3 audio to text
        transcribe_audio(audio_path, video_id)

        # Generating summary of the text file
        loader = TextLoader(transcript_filepath, encoding='utf8')
        documents = loader.load()
        
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        db = Chroma.from_documents(texts, embeddings)

        retriever = db.as_retriever()
        qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
        answer = qa.run(question)

    return answer.strip()
    
# Function to Generate Summary from Transcript
def generate_video_summary(api_key, url):

    openai.api_key = api_key

    llm = OpenAI(temperature=0, openai_api_key=api_key, model_name="gpt-3.5-turbo")
    text_splitter = CharacterTextSplitter()

    # Extract the video_id from the url
    query = urlparse(url).query
    params = parse_qs(query)
    video_id = params["v"][0]

    # The path of the audio file
    audio_path = f"tmp/{video_id}.mp3"

    # The path of the transcript
    transcript_filepath = f"tmp/{video_id}.txt"

    # Check if the transcript file already exist
    if os.path.exists(transcript_filepath):
        # Generating summary of the text file
        with open(transcript_filepath) as f:
            transcript_file = f.read()

        texts = text_splitter.split_text(transcript_file)
        docs = [Document(page_content=t) for t in texts[:3]]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = chain.run(docs)
    
    else: 
        download_audio(url)

        # Transcribe the mp3 audio to text
        transcribe_audio(audio_path, video_id)

        # Generating summary of the text file
        with open(transcript_filepath) as f:
            transcript_file = f.read()

        texts = text_splitter.split_text(transcript_file)
        docs = [Document(page_content=t) for t in texts[:3]]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = chain.run(docs)

    return summary.strip()
