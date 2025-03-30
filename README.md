# ayurveda
An Ai Assistant which tells you the goodness of nature and how you can prevent and cure diseases.


# How to run?
### steps:

Clone the repository


```bash
git clone https://github.com/Anindya2369/ayurveda.git
```

### step 01- Create a conda environment after opening the repository

```bash
conda create -n herbbot python=3.8 -y
```
```bash 
conda activate herbbot
```


### step 02-  Install the requirements

```bash
pip install -r requirements.txt
```
### create a '.env' file in the root directory and add your Pinecone, OpenAI, and SERP API credentials as follow:

```ini
PINECONE_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OPENAI_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SERP_API_KEY = "YOUR_SERP_API_KEY"
```

The SERP API key is required for the Google search fallback functionality, which allows the assistant to retrieve up-to-date information when it doesn't have sufficient context in its knowledge base.

### create the knowledge base for the bot:

```bash
# run the following command to create embeddings and store them to pinecone.

python store_index.py
```

### Intialize the bot's backend and frontend:

```bash

python app.py
```

### Check the app deployed on localhost:

```bash
open up localhost:
```

### Techstack Used:

- Python
- LangChain
- Flask
- groq_client
- Pinecone
