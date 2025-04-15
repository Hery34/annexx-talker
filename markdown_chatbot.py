# markdown_chatbot.py
import os
import glob
import numpy as np
import openai
from dotenv import load_dotenv

class MarkdownChatbot:
    def __init__(self, docs_dir, openai_api_key=None):
        """Initialise le chatbot avec les documents markdown."""
        self.docs_dir = docs_dir
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
        # Charger les documents et créer les embeddings
        self.documents = self._load_markdown_docs()
        print(f"Nombre de segments de documents chargés: {len(self.documents)}")
        
        # Créer les embeddings (vecteurs) des documents
        self.embeddings = self._create_embeddings(self.documents)
        
        # Historique de conversation
        self.chat_history = []
    
    def _load_markdown_docs(self):
        """Charge et divise les documents markdown."""
        print("Chargement des documents Markdown...")
        
        # Trouver tous les fichiers markdown
        markdown_files = glob.glob(os.path.join(self.docs_dir, "**/*.md"), recursive=True)
        
        if not markdown_files:
            raise ValueError(f"Aucun fichier Markdown trouvé dans {self.docs_dir}")
            
        print(f"Nombre de fichiers Markdown trouvés: {len(markdown_files)}")
        
        # Charger et diviser les documents
        documents = []
        
        for file_path in markdown_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # Diviser en segments de 1000 caractères avec 100 caractères de chevauchement
                    for i in range(0, len(content), 900):
                        chunk = content[i:i+1000]
                        # Ajouter des métadonnées pour traçabilité
                        documents.append({
                            "content": chunk,
                            "source": file_path
                        })
                    print(f"Chargé: {file_path} - {len(content)} caractères")
            except Exception as e:
                print(f"Erreur lors du chargement de {file_path}: {e}")
                
        return documents
    
    def _create_embeddings(self, documents):
        """Crée des embeddings pour tous les documents."""
        print("Création des embeddings...")
        
        # Extraire le texte des documents
        texts = [doc["content"] for doc in documents]
        
        # Créer des embeddings par lots de 20 pour éviter les limites d'API
        all_embeddings = []
        batch_size = 20
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            try:
                response = openai.embeddings.create(
                    model="text-embedding-ada-002",
                    input=batch_texts
                )
                batch_embeddings = [embedding.embedding for embedding in response.data]
                all_embeddings.extend(batch_embeddings)
                print(f"Embeddings créés: {i+len(batch_texts)}/{len(texts)}")
            except Exception as e:
                print(f"Erreur lors de la création des embeddings pour le lot {i}: {e}")
                # Créer des embeddings vides en cas d'erreur
                all_embeddings.extend([np.zeros(1536) for _ in range(len(batch_texts))])
        
        return all_embeddings
    
    def _find_relevant_documents(self, query, top_k=3):
        """Trouve les documents les plus pertinents pour la requête."""
        # Créer l'embedding de la requête
        query_response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=[query]
        )
        query_embedding = query_response.data[0].embedding
        
        # Calculer la similarité avec tous les documents
        similarities = []
        for doc_embedding in self.embeddings:
            # Similarité cosinus
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append(similarity)
        
        # Trouver les indices des documents les plus similaires
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Retourner les documents pertinents
        relevant_docs = [self.documents[i] for i in top_indices]
        return relevant_docs
    
    def ask(self, query):
        """Répond à une question en utilisant les documents pertinents."""
        try:
            # Trouver les documents pertinents
            relevant_docs = self._find_relevant_documents(query)
            
            # Construire le contexte à partir des documents pertinents
            context = "\n\n---\n\n".join([doc["content"] for doc in relevant_docs])
            
            # Construire les messages pour le chat
            messages = [
                {"role": "system", "content": f"Vous êtes un assistant IA basé sur une collection de documents markdown. "
                                            f"Répondez aux questions en utilisant uniquement les informations contenues "
                                            f"dans ces documents. Si la réponse n'est pas dans les documents, dites que "
                                            f"vous ne savez pas. Voici les extraits pertinents:\n\n{context}"}
            ]
            
            # Ajouter l'historique récent (limité à 4 messages)
            for msg in self.chat_history[-4:]:
                messages.append(msg)
            
            # Ajouter la question actuelle
            messages.append({"role": "user", "content": query})
            
            # Générer la réponse
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content
            
            # Mettre à jour l'historique
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": answer})
            
            return answer
        
        except Exception as e:
            return f"Erreur lors du traitement de votre question: {str(e)}"
    
    def reset_conversation(self):
        """Réinitialise l'historique de conversation."""
        self.chat_history = []
        return "Conversation réinitialisée."