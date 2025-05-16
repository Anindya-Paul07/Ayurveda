from setuptools import setup

setup(
    name='AyurvedaBackend',
    version='0.0.1',
    packages=['back'],
    install_requires=[
        'flask==2.3.3',
        'flask_cors==4.0.0',
        'python-dotenv==1.0.0',
        'langchain==0.0.300',
        'langchain-community==0.0.300',
        'langchain-openai==0.0.300',
        'langchain-pinecone==0.0.300',
        'openai==1.3.0',
        'pinecone-client[grpc]==3.2.2'
    ],
    entry_points={
        'console_scripts': [
            'ayurveda-backend=back.app:app'
        ]
    }
)
