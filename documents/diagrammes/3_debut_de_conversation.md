
## 1. Points d'Entrée Multiples
- **2ième passage/demande**: Client qui revient avec une nouvelle demande
- **Retour horaires**: Demande spécifique liée aux horaires
- **Mode LLM**: Traitement via modèle de langage

## 2. Gestion de la Conversation
- **Second message relance**: Suivi automatique
- **Début conv start**:
    - **[FIRSTMESSAGE]**: Message d'accueil standard
    - **[QUESTION]**: Qualification de la demande

## 3. Politique d'Enregistrement
- **STAT enregistrements conversations refusés**:
    - Options: **répéter**, **refuser**, **Other**
- **NE PAS ENREGISTRER RECORDING**: Directive de non-enregistrement
- **Prompt**: Confirmation au client que la conversation n'est pas enregistrée


## 5. Identification des Limites du LLM
**Questions généralement non comprises par GPT**:

- Identification des cas où l'automatisation est insuffisante
- Sert à éviter des tentatives de traitement automatique vouées à l'échec


