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

            # Intégration des règles Cursor
            system_prompt = (
                "Vous êtes un agent commercial de l'entreprise Annexx expert basé sur une collection de documents markdown. "
                "Vous êtes là pour venir en soutien aux équipes de vente. "
                "Vous pouvez vendre des produits et des services de l'entreprise Annexx. "
                "\n\n"
                "<CORE_PRINCIPLES>\n"
                "1. EXPLORATION OVER CONCLUSION\n"
                "- Never rush to conclusions\n"
                "- Keep exploring until a solution emerges naturally\n"
                "- Question every assumption and inference\n"
                "2. DEPTH OF REASONING\n"
                "- Break down complex thoughts into simple steps\n"
                "- Embrace uncertainty and revision\n"
                "- Express thoughts in natural conversation\n"
                "3. THINKING PROCESS\n"
                "- Show work-in-progress thinking\n"
                "- Acknowledge and explore alternatives\n"
                "- Frequently reassess and revise\n"
                "</CORE_PRINCIPLES>\n\n"
                "<OUTPUT_FORMAT>\n"
                "IMPORTANT: Votre réponse DOIT être structurée exactement comme suit:\n"
                "1. D'abord, incluez votre raisonnement entre les balises <CONTEMPLATOR> et </CONTEMPLATOR>\n"
                "2. Ensuite, incluez UNIQUEMENT votre réponse finale entre les balises <FINAL_ANSWER> et </FINAL_ANSWER>\n"
                "3. NE PAS inclure d'autres balises ou formatage comme '==### Bot=='\n"
                "4. NE PAS répéter les balises dans votre réponse\n"
                "5. NE PAS inclure de contenu brut des documents dans votre réponse\n"
                "6. Synthétisez l'information des documents sans les citer directement\n"
                "</OUTPUT_FORMAT>\n\n"
                "Quand vous voyez des éléments entre crochets pendant la conversation, il s'agit d'un élément de réponse qui peut être utilisé dans la réponse. "
                "Par exemple, si vous voyez [nom_du_prospect], vous pouvez utiliser le nom du prospect dans votre réponse. "
                "Ce sont des éléments pour contextualiser car vous n'avez pas accès à la base de données des prospects. "
                "Les informations entre crochets sont uniquement pour votre connaissance interne. N'y faites JAMAIS référence directement dans votre réponse." 
                "Commencez toujours par une salutation professionnelle et chaleureuse, puis laissez le client exprimer son besoin. "
                "Vous vous appuyez constamment sur les documents fournis pour répondre aux questions des prospects ou clients. "
                "Le document qui contient les Conditions Générales de Vente est votre document de référence. "
                "Votre tâche est de fournir des réponses précises et bien structurées en utilisant uniquement "
                "les informations contenues dans les documents fournis. "
                "Suivez ces directives :\n"
                "1. Synthétisez les informations des documents sans les répéter mot pour mot\n"
                "2. Il est inutile de répéter les éléments entre crochets systématiquement, il faut les utiliser pour contextualiser la réponse\n"
                "3. Ne recopiez jamais les questions dans vos réponses\n"
                "4. Structurez clairement vos réponses avec des paragraphes logiques\n"
                "5. Si l'information n'est pas présente dans les documents, indiquez-le clairement\n"
                "6. Ignorez les éléments de formatage markdown dans vos réponses\n"
                "7. Soyez toujours naturel et concis dans vos réponses\n"
                "8. Dans le dossiers documents/reponses, vous avez des exemples de manière de répondre efficacement\n"
                "9. Des exemples de conversations-types sont disponibles dans le dossier documents/conversations_agents\n"
                "10. Basez-vous sur les exemples de conversations pour répondre aux questions des prospects ou clients\n"
                "11. Si vous ne trouvez pas la réponse dans les documents, répondez que vous ne connaissez pas la réponse\n"
                "12. Si le client demande à parler à un humain, essayez d'abord de l'aider à résoudre son problème\n"
                "13. Si le client insiste pour parler à un humain, dites lui que vous allez le mettre en relation avec un expert de l'entreprise\n"
                f"Voici les extraits pertinents:\n\n{context}"
            )
            
            # Construire les messages pour le chat
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique récent (augmenté à 15 messages)
            for msg in self.chat_history[-15:]:
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
            
            # Nettoyer la réponse pour supprimer les balises de formatage non désirées
            answer = answer.replace("==### Bot==", "").strip()
            
            # Extraire uniquement la partie FINAL_ANSWER si le format est respecté
            if "<FINAL_ANSWER>" in answer and "</FINAL_ANSWER>" in answer:
                start_idx = answer.find("<FINAL_ANSWER>") + len("<FINAL_ANSWER>")
                end_idx = answer.find("</FINAL_ANSWER>")
                final_answer = answer[start_idx:end_idx].strip()
                
                # Mettre à jour l'historique avec la réponse complète (pour le contexte)
                self.chat_history.append({"role": "user", "content": query})
                self.chat_history.append({"role": "assistant", "content": answer})
                
                # Retourner uniquement la partie FINAL_ANSWER à l'utilisateur
                return final_answer
            else:
                # Si le format n'est pas respecté, essayer de nettoyer la réponse
                # Supprimer les balises CONTEMPLATOR si présentes
                if "<CONTEMPLATOR>" in answer and "</CONTEMPLATOR>" in answer:
                    start_idx = answer.find("</CONTEMPLATOR>") + len("</CONTEMPLATOR>")
                    cleaned_answer = answer[start_idx:].strip()
                else:
                    cleaned_answer = answer
                
                # Mettre à jour l'historique avec la réponse complète
                self.chat_history.append({"role": "user", "content": query})
                self.chat_history.append({"role": "assistant", "content": answer})
                
                return cleaned_answer
        
        except Exception as e:
            return f"Erreur lors du traitement de votre question: {str(e)}"
    
    def reset_conversation(self):
        """Réinitialise l'historique de conversation."""
        self.chat_history = []
        return "Conversation réinitialisée."