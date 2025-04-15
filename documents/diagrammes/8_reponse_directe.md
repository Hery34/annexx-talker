## Vue d'ensemble
Ce document formalise le flux de conversation pour le traitement des réponses directes dans le système de dialogue automatisé. Ce segment se concentre sur les requêtes qui peuvent être résolues immédiatement par consultation d'une FAQ ou qui nécessitent un traitement rapide, sans passer par le processus complet d'authentification par SMS.

## 1. Réception de la requête directe
1. **Sujet avec réponse directe** : Point d'entrée du flux pour les requêtes nécessitant une réponse immédiate
    - Identifie automatiquement les sujets pouvant être traités directement


## 2. Recherche de réponse
1. **API cherche une réponse type dans FAQ Annexe** : Interrogation de la base de connaissances
    - Consultation automatique des réponses préenregistrées
    - Api Call : Appel API pour récupérer l'information pertinente
2. **Set Condition** : Évaluation de la disponibilité d'une réponse
    - **Vrai** : Une réponse appropriée a été trouvée dans la FAQ
    - **Faux** : Aucune réponse satisfaisante n'a été identifiée

## 3. Délivrance de la réponse
**réponse Bot** : Présentation de la réponse automatisée à l'utilisateur

- **[BOTANSWER]** : Contenu généré par le système avec la formule "Avez-vous besoin..."
- **[QUESTION]** : Format interrogatif pour encourager l'interaction

## 4. Gestion post-réponse
1. **répéter la réponse** : Options après délivrance de la première réponse
    - Redirection based on keyword : Analyse des mots-clés dans la réponse de l'utilisateur
    - Options de réponse :
        - **répéter** : L'utilisateur demande une répétition de l'information
        - **Other** : Autre situation nécessitant un traitement spécifique
2. **redirection** : Réorientation de la conversation selon le contexte

## 5. Transfert vers service humain
**transfert agence/CAC** : Redirection vers un agent humain

- Apparaît à plusieurs endroits du flux comme solution de repli
- Peut être déclenché après une réponse Bot ou dans d'autres contextes

## 6. Segment de paiement 
### Entrée paiement

1. **payer** : Point d'entrée spécifique pour les questions liées au paiement
    - Accessible directement pour les requêtes financières

### Analyse de la demande

1. **Redirection en [QUESTION]** : Catégorisation de la question de paiement
    - Redirection based on keyword : Analyse des termes spécifiques au paiement
    - Options principales :
        - **payer en avance** : Demandes de paiement anticipé
        - **Other** : Autres questions de paiement

## 7. Vérification et confirmation

- **transfert agence/CAC** : Pour les questions complexes de paiement
    - Redirection vers un agent spécialisé
- **Confirmation identité** : Vérification d'identité pour les transactions sensibles
    - Étape de sécurité supplémentaire avant de procéder à des opérations financières