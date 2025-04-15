import os
import glob
from typing import List
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import MarkdownTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Charger les variables d'environnement
load_dotenv()

class MarkdownChatbot:
    def __init__(self, docs_dir: str, openai_api_key: str = None):
        """
        Initialise l'agent conversationnel avec les documents Markdown.
        
        Args:
            docs_dir: Chemin vers le dossier contenant les documents Markdown
            openai_api_key: Clé API OpenAI (optionnel si définie dans .env)
        """
        self.docs_dir = docs_dir
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set it in .env file or pass it directly.")
            
        # Initialiser les composants
        self.documents = self._load_markdown_docs()
        self.vectorstore = self._create_vectorstore()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.qa_chain = self._create_qa_chain()
        
    def _load_markdown_docs(self) -> List:
        """Charge tous les documents Markdown et les divise en chunks."""
        print("Chargement des documents Markdown...")
        
        # Trouver tous les fichiers markdown
        markdown_files = glob.glob(os.path.join(self.docs_dir, "**/*.md"), recursive=True)
        
        if not markdown_files:
            raise ValueError(f"Aucun fichier Markdown trouvé dans {self.docs_dir}")
            
        print(f"Nombre de fichiers Markdown trouvés: {len(markdown_files)}")
        
        # Charger et diviser les documents
        documents = []
        
        # Configurez le diviseur de texte pour les documents Markdown
        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
        
        for file_path in markdown_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    chunks = text_splitter.split_text(content)
                    documents.extend(chunks)
                    print(f"Chargé: {file_path} - {len(chunks)} chunks")
            except Exception as e:
                print(f"Erreur lors du chargement de {file_path}: {e}")
                
        return documents
    
    def _create_vectorstore(self):
        """Crée un index vectoriel des documents pour une recherche efficace."""
        print("Création de l'index vectoriel...")
        
        # Initialiser les embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        
        # Créer un vectorstore à partir des documents
        vectorstore = FAISS.from_texts(self.documents, embeddings)
        
        return vectorstore
    
    def _create_qa_chain(self):
        """Crée la chaîne de traitement question-réponse."""
        # Initialiser le modèle de langage
        llm = ChatOpenAI(
            temperature=0.7, 
            model_name="gpt-4", 
            openai_api_key=self.openai_api_key
        )
        
        # Créer la chaîne de retrieval QA
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            chain_type="stuff",
            verbose=True
        )
        
        return qa_chain
    
    def ask(self, query: str) -> str:
        """
        Pose une question à l'agent et obtient une réponse.
        
        Args:
            query: La question à poser
            
        Returns:
            La réponse générée par l'agent
        """
        if not query.strip():
            return "Veuillez poser une question."
        
        try:
            # Obtenir une réponse basée sur la question et l'historique de conversation
            response = self.qa_chain({"question": query})
            return response["answer"]
        except Exception as e:
            return f"Erreur lors du traitement de votre question: {str(e)}"

    def reset_conversation(self):
        """Réinitialise l'historique de conversation."""
        self.memory.clear()
        return "Conversation réinitialisée."