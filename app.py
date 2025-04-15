# app.py
import streamlit as st
import os
from markdown_chatbot import MarkdownChatbot

# Configuration de la page
st.set_page_config(
    page_title="Assistant Documents Markdown",
    page_icon="💬",
    layout="wide"
)

# Titre de l'application
st.title("💬 Agent conversationnel Annexx")

# Initialisation des variables de session
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration")
    
    # Input pour la clé API OpenAI
    openai_api_key = st.text_input("Clé API OpenAI", 
                                  type="password", 
                                  help="Votre clé API OpenAI est nécessaire")
    
    # Input pour le chemin des documents
    docs_dir = st.text_input("Dossier des documents Markdown", 
                            value="./documents",
                            help="Chemin vers le dossier contenant vos documents")
    
    # Bouton pour initialiser le chatbot
    if st.button("Initialiser l'assistant"):
        if not openai_api_key:
            st.error("Veuillez fournir une clé API OpenAI")
        elif not os.path.exists(docs_dir):
            st.error(f"Le dossier {docs_dir} n'existe pas")
        else:
            with st.spinner("Initialisation de l'assistant (création des embeddings, cela peut prendre quelques instants)..."):
                try:
                    st.session_state.chatbot = MarkdownChatbot(docs_dir, openai_api_key)
                    st.success("Assistant initialisé avec succès!")
                    # Réinitialiser l'historique des messages dans l'interface
                    st.session_state.messages = []
                except Exception as e:
                    st.error(f"Erreur lors de l'initialisation: {str(e)}")
    
    # Bouton pour réinitialiser la conversation
    if st.button("Réinitialiser la conversation"):
        if st.session_state.chatbot:
            st.session_state.chatbot.reset_conversation()
            st.session_state.messages = []
            st.success("Conversation réinitialisée!")

# Affichage des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pour la question
if prompt := st.chat_input("Posez votre question..."):
    # Vérifier si le chatbot est initialisé
    if not st.session_state.chatbot:
        st.error("Veuillez initialiser l'assistant dans la barre latérale")
    else:
        # Ajouter la question de l'utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Afficher la question de l'utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Obtenir et afficher la réponse du chatbot
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                response = st.session_state.chatbot.ask(prompt)
                st.markdown(response)
                
        # Ajouter la réponse à l'historique
        st.session_state.messages.append({"role": "assistant", "content": response})

# Informations d'utilisation
if not st.session_state.chatbot:
    st.info("""
    ### Comment utiliser cet assistant:
    
    1. Configurez l'assistant dans la barre latérale:
       - Entrez votre clé API OpenAI
       - Spécifiez le chemin vers votre dossier de documents Markdown
       - Cliquez sur "Initialiser l'assistant"
    
    2. Posez vos questions dans la zone de saisie en bas de l'écran
    
    3. L'assistant vous répondra en se basant sur le contenu de vos documents
    """)