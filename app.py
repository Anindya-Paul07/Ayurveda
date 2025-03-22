from flask import Flask, render_template, jsonify, request
from service.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from service.prompt import system_prompt
from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI

app = Flask(__name__)
load_dotenv()

# Validate environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([PINECONE_API_KEY, OPENAI_API_KEY]):
    missing = [k for k in ["PINECONE_API_KEY", "OPENAI_API_KEY"] if not os.getenv(k)]
    raise RuntimeError(f"Missing environment variables: {missing}")

# Initialize Groq client
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=OPENAI_API_KEY
)

# Initialize LangChain components
embeddings = download_hugging_face_embeddings()
index_name = "herbbot"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = ChatOpenAI(
    openai_api_base="https://api.groq.com/openai/v1",
    model_name="llama-3.3-70b-versatile",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.4,
    max_tokens=500
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

@app.route("/")
def index():
    return render_template("ayurveda_chat.html")

@app.route("/get", methods=["POST"])
def chat():
    try:
        user_input = request.form["msg"]
        print(f"User input: {user_input}")
        
        # Using RAG chain
        result = rag_chain.invoke({"input": user_input})
        answer = result["answer"]
        
        print(f"Generated answer: {answer}")
        return jsonify({
            "response": answer,
             "sources": [doc.metadata.get("source", "") for doc in result["context"]]
                        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=2222, debug=True)