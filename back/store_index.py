"""
Store Index Script
-----------------
This script handles the process of loading Ayurvedic knowledge from PDF files,
processing the text, generating embeddings, and storing them in a Pinecone vector database.
This enables semantic search capabilities for the Ayurveda application.
"""

from back.service.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get Pinecone API key from environment variables
PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


# Step 1: Load PDF files from the Data directory
# This extracts all text content from Ayurvedic knowledge PDFs
extracted_data=load_pdf_file(data='Data/')

# Step 2: Split the extracted text into manageable chunks for processing
# This creates smaller text segments that can be effectively embedded
text_chunks=text_split(extracted_data)

# Step 3: Download and initialize the Hugging Face embedding model
# This model converts text chunks into numerical vector representations
embeddings = download_hugging_face_embeddings()


# Step 4: Initialize Pinecone client with API key
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name for our Ayurvedic knowledge base
index_name = "herbbot"


# Step 5: Create a new Pinecone vector index if it doesn't exist
# This index will store all our text embeddings for semantic search
pc.create_index(
    name=index_name,
    dimension=384,  # Dimension size of the Hugging Face embeddings
    metric="cosine",  # Similarity metric for comparing vectors
    spec=ServerlessSpec(
        cloud="aws",  # Cloud provider
        region="us-east-1"  # AWS region for the serverless index
    ) 
) 

# Step 6: Convert text chunks to embeddings and store them in Pinecone
# This creates a searchable vector database of our Ayurvedic knowledge
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,  # The text chunks to be embedded
    index_name=index_name,  # The name of our Pinecone index
    embedding=embeddings,   # The embedding model to use
)

# The index is now populated with vector embeddings of Ayurvedic knowledge
# and ready to be queried by the application for semantic search capabilities
"""
Store Index Script
-----------------
This script handles the process of loading Ayurvedic knowledge from PDF files,
processing the text, generating embeddings, and storing them in a Pinecone vector database.
This enables semantic search capabilities for the Ayurveda application.
"""

from back.service.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Get Pinecone API key from environment variables
PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


# Step 1: Load PDF files from the Data directory
# This extracts all text content from Ayurvedic knowledge PDFs
extracted_data=load_pdf_file(data='Data/')

# Step 2: Split the extracted text into manageable chunks for processing
# This creates smaller text segments that can be effectively embedded
text_chunks=text_split(extracted_data)

# Step 3: Download and initialize the Hugging Face embedding model
# This model converts text chunks into numerical vector representations
embeddings = download_hugging_face_embeddings()


# Step 4: Initialize Pinecone client with API key
pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name for our Ayurvedic knowledge base
index_name = "herbbot"


# Step 5: Create a new Pinecone vector index if it doesn't exist
# This index will store all our text embeddings for semantic search
pc.create_index(
    name=index_name,
    dimension=384,  # Dimension size of the Hugging Face embeddings
    metric="cosine",  # Similarity metric for comparing vectors
    spec=ServerlessSpec(
        cloud="aws",  # Cloud provider
        region="us-east-1"  # AWS region for the serverless index
    ) 
) 

# Step 6: Convert text chunks to embeddings and store them in Pinecone
# This creates a searchable vector database of our Ayurvedic knowledge
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,  # The text chunks to be embedded
    index_name=index_name,  # The name of our Pinecone index
    embedding=embeddings,   # The embedding model to use
)

# The index is now populated with vector embeddings of Ayurvedic knowledge
# and ready to be queried by the application for semantic search capabilities
