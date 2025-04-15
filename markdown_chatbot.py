# markdown_chatbot.py
import os
import glob
import math
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
                all_embeddings.extend([[0.0] * 1536 for _ in range(len(batch_texts))])
        
        return all_embeddings
    
    def _cosine_similarity(self, vec1, vec2):
        """Calcule la similarité cosinus entre deux vecteurs sans NumPy."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        
        if norm_a == 0 or norm_b == 0:
            return 0  # Éviter division par zéro
            
        return dot_product / (norm_a * norm_b)
    
    def _find_relevant_documents(self, query, top_k=5):
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
            # Similarité cosinus sans NumPy
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Trouver les indices des documents les plus similaires
        # Version sans NumPy
        indexed_similarities = [(i, sim) for i, sim in enumerate(similarities)]
        sorted_indices = sorted(indexed_similarities, key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in sorted_indices[:top_k]]
        
        # Retourner les documents pertinents
        relevant_docs = [self.documents[i] for i in top_indices]
        return relevant_docs
    
    def ask(self, query):
        """Répond à une question en utilisant les documents pertinents."""
        try:
            # Trouver les documents pertinents
            relevant_docs = self._find_relevant_documents(query, top_k=5)
            
            # Construire le contexte à partir des documents pertinents
            context_parts = [] 
            for doc in relevant_docs:
                context_parts.append(f"Document: {os.path.basename(doc['source'])}\n{doc['content']}")
            
            context = "\n\n---\n\n".join(context_parts)

            system_prompt = (
                "Vous êtes un agent commercial de l'entreprise Annexx expert basé sur une collection de documents markdown. "
                "Vous êtes là pour venir en soutien aux équipes de vente . "
                "Vous pouvez vendre des produits et des services de l'entreprise Annexx. "
                "Qund tu vois des éléments entre crochets pendant la conversation, il s'agit d'un élément de réponse qui peut être utilisé dans la réponse. "
                "Par exemple, si tu vois [nom_du_prospect], tu peux utiliser le nom du prospect dans ta réponse. "
                "Ce sont des éléments pour contextualiser car tu n'as pas accès à la base de données des prospects. "
                "Vous vous appuyez constamment sur les documents fournis pour répondre aux questions des prospects ou clients."
                "Le document qui contient les Conditions Générales de Vente est votre document de référence."
                "Vous pouvez répondre à toutes les questions des prospects ou clients."
                "Votre tâche est de fournir des réponses précises et bien structurées en utilisant uniquement "
                "les informations contenues dans les documents fournis. "
                "Suivez ces directives :\n"
                "1. Synthétisez les informations des documents sans les répéter mot pour mot\n"
                "2. Ne recopiez jamais les questions dans vos réponses\n"
                "3. Structurez clairement vos réponses avec des paragraphes logiques\n"
                "4. Si l'information n'est pas présente dans les documents, indiquez-le clairement\n"
                "5. Ignorez les éléments de formatage markdown dans vos réponses\n\n"
                "6. Soyez toujours naturel et concis dans vos réponses\n\n"
                "7. Dans le dossiers documents/reponses, vous avez des exemples de manière de répondre efficacement\n\n"
                "8. Des exemples de conversations-types types sont disponibles dans le dossier documents/conversations_agents\n\n"
                "9. Basez-vous sur les exemples de conversations pour répondre aux questions des prospects ou clients\n\n"
                "10. Si vous ne trouvez pas la réponse dans les documents, répondez que vous ne connaissez pas la réponse.\n\n"
                "11. Si le client demande à parler à un humain, essayez d'abord de l'aider à résoudre son problème.\n\n"
                "12. Si le client insiste pour parler à un humain, dites lui que vous allez le mettre en relation avec un expert de l'entreprise.\n\n"
                f"Voici les extraits pertinents:\n\n{context}"
            )
            
            # Construire les messages pour le chat
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique récent (limité à 4 messages)
            for msg in self.chat_history[-6:]:
                messages.append(msg)
            
            # Ajouter la question actuelle
            messages.append({"role": "user", "content": query})
            
            # Générer la réponse
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
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