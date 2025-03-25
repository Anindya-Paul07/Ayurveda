from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()

from service.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from service.prompt import system_prompt
from openai import OpenAI
from langchain_openai import ChatOpenAI



def initialize_components():
    # Validate environment variables
    pinecone_key = os.getenv("PINECONE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not all([pinecone_key, openai_key]):
        missing = [k for k in ["PINECONE_API_KEY", "OPENAI_API_KEY"] if not os.getenv(k)]
        raise RuntimeError(f"Missing environment variables: {missing}")

    # Initialize components
    embeddings = download_hugging_face_embeddings()
    
    return {
        "retriever": PineconeVectorStore.from_existing_index(
            index_name="herbbot",
            embedding=embeddings
        ).as_retriever(search_kwargs={"k": 3}),
        "llm": ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            model_name="llama-3.3-70b-versatile",
            openai_api_key=openai_key,
            temperature=0.4,
            max_tokens=500
        )
    }

# Initialize components on first request
@app.before_request
def setup_chain():
    components = initialize_components()
    app.config["rag_chain"] = create_retrieval_chain(
        components["retriever"],
        create_stuff_documents_chain(
            components["llm"],
            ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
        )
    )

@app.route("/")
def index():
    return render_template("ayurveda_chat.html")

@app.route("/get", methods=["POST"])
def chat():
    try:
        user_input = request.form["msg"]
        result = app.config["rag_chain"].invoke({"input": user_input})
        
        return jsonify({
            "response": result["answer"],
            "sources": [doc.metadata.get("source", "") for doc in result["context"]]
        })
    
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=2222, debug=True)