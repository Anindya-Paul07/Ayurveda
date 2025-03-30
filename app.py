from flask import Flask, render_template, jsonify, request
from service.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from service.prompt import *
from service.google_search import execute_google_search
import os
import re

# Enhanced data structure to store tracked diseases and their remedies
tracked_diseases = {}

def track_disease(user_msg, bot_answer):
    # Define a list of common disease keywords; expand as needed
    disease_keywords = ['diabetes', 'hypertension', 'cancer', 'asthma', 'arthritis']
    for disease in disease_keywords:
        if disease in user_msg.lower() or disease in bot_answer.lower():
            # Initialize the disease entry with a structured format if it doesn't exist
            if disease not in tracked_diseases:
                tracked_diseases[disease] = {
                    'full_responses': [],
                    'remedies': []
                }
            
            # Add the full response
            tracked_diseases[disease]['full_responses'].append(bot_answer)
            
            # Try to extract remedy-specific information
            extract_remedies(disease, bot_answer)

def extract_remedies(disease, bot_answer):
    """Extract remedy information from bot answers and store it separately"""
    # Common patterns that might indicate remedies in the text
    remedy_indicators = [
        r"(?:recommended|common|effective|useful|beneficial) (?:remedies|treatments|herbs|solutions)",
        r"(?:you can|try|consider) (?:using|taking|consuming)",
        r"(?:home remedies|natural treatments)",
        r"(?:ayurvedic treatments|herbs for)"
    ]
    
    # Check if any remedy indicator is present in the answer
    contains_remedy = any(re.search(pattern, bot_answer.lower()) for pattern in remedy_indicators)
    
    if contains_remedy:
        # If the answer likely contains remedy information, add it to the remedies list
        if bot_answer not in tracked_diseases[disease]['remedies']:
            tracked_diseases[disease]['remedies'].append(bot_answer)

app = Flask(__name__)

load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY=os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

embeddings = download_hugging_face_embeddings()


index_name = "herbbot"

# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})


llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="llama-3.3-70b-versatile",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.4,
            max_tokens=1024
        )
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def index():
    return render_template('ayurveda_chat.html', diseases=tracked_diseases)


@app.route("/api/general", methods=["GET", "POST"])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input"}), 400
    msg = data.get('message')
    print(f"Received message: {msg}")
    response = rag_chain.invoke({"input": msg})
    answer = response.get("answer")
    # Check if the local context was insufficient
    if not answer or "don't know" in answer.lower() or "i don't have" in answer.lower():
        google_result = execute_google_search(msg)
        answer = f"Based on additional research, here are some results:\n\n{google_result}"
    print(f"Response: {answer}")
    
    # Track diseases and remedies mentioned in the conversation
    track_disease(msg, answer)
    track_remedy(msg, answer)
    
    return jsonify({"response": answer})

def track_remedy(user_msg, bot_answer):
    """
    Dedicated function to identify and track potential remedies in bot answers
    This function analyzes the bot's response for specific remedy patterns
    """
    # Look for specific remedy patterns in the answer
    remedy_patterns = [
        # Pattern for lists of remedies
        r"\d+\.\s+([^.]+)",
        # Pattern for "take X for Y" statements
        r"take\s+([^.]+)\s+for\s+([^.]+)",
        # Pattern for "X is beneficial for Y" statements
        r"([^.]+)\s+is\s+beneficial\s+for\s+([^.]+)",
        # Pattern for "X helps with Y" statements
        r"([^.]+)\s+helps\s+with\s+([^.]+)"
    ]
    
    # Check for disease mentions in the user message or bot answer
    disease_keywords = ['diabetes', 'hypertension', 'cancer', 'asthma', 'arthritis','cold fever','cancer','tumor']
    mentioned_diseases = []
    
    for disease in disease_keywords:
        if disease in user_msg.lower() or disease in bot_answer.lower():
            mentioned_diseases.append(disease)
    
    # If no specific disease is mentioned, check for general remedy information
    if not mentioned_diseases:
        if any(re.search(pattern, bot_answer) for pattern in remedy_patterns):
            if "general_remedies" not in tracked_diseases:
                tracked_diseases["general_remedies"] = {
                    'full_responses': [],
                    'remedies': []
                }
            tracked_diseases["general_remedies"]['full_responses'].append(bot_answer)
            tracked_diseases["general_remedies"]['remedies'].append(bot_answer)
    else:
        # For each mentioned disease, check if the answer contains remedy information
        for disease in mentioned_diseases:
            # Ensure the disease entry exists with the proper structure
            if disease not in tracked_diseases:
                tracked_diseases[disease] = {
                    'full_responses': [],
                    'remedies': []
                }
            
            # Check if the answer contains specific remedy patterns
            if any(re.search(pattern, bot_answer) for pattern in remedy_patterns):
                # Add to remedies if not already present
                if bot_answer not in tracked_diseases[disease]['remedies']:
                    tracked_diseases[disease]['remedies'].append(bot_answer)




@app.route('/api/remedies', methods=['GET'])
def get_remedies():
    # Create a simplified version of tracked_diseases for the frontend
    # The frontend expects a structure where each disease maps to a list of remedies
    simplified_remedies = {}
    
    for disease, data in tracked_diseases.items():
        # If we have specific remedies extracted, use those
        if data['remedies']:
            simplified_remedies[disease] = data['remedies']
        # Otherwise fall back to full responses
        elif data['full_responses']:
            simplified_remedies[disease] = data['full_responses']
    
    return jsonify(simplified_remedies)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)
