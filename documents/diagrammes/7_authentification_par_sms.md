
## Vue d'ensemble
Ce document formalise le flux de conversation d'un système automatisé d'authentification et de vérification d'identité par SMS. Le système gère l'envoi de codes PIN par SMS, les réponses des utilisateurs, et les différentes redirections basées sur les interactions.

## Variables du système

Le système utilise plusieurs variables clés pour gérer le flux de conversation :

- **LOOP** : Contrôle les boucles de dialogue
- **CODEPIN** : Stocke le code PIN envoyé à l'utilisateur
- **TAG** : Identifie certains segments de conversation
- **STT** : Variable liée au service URLIVE (possiblement Speech-to-Text)
- **TT** : Variables auxiliaires (TT1, TT2)
- **NUMEROMOBILEVRIF** : Stocke le numéro mobile vérifié

## 1. Initialisation
- **Set variable [LOOP]** : Initialisation de la variable de boucle
- **Mobile déjà vérifié ?** : Condition qui détermine le chemin initial
    - **Vrai** : Continue vers la redirection après identif
    - **Faux** : Procède à la vérification

## 2. Processus d'envoi du code
- **code pin envoyé par SMS** : Système envoie un code PIN
    - Set variable Value : Enregistre le code envoyé
- **sendSMSToCustomer SMS** : Action d'envoi du SMS
    - Adresse email code : Possibilité d'envoyer aussi par email

## 3. Vérification et attente
- **changer le SST avec URLIVE** : Modification du système de dialogue
    - d'accord afin de vous répondre [...] : Message d'attente
- **prêt à recevoir le SMS d'identification** : État d'attente pour l'utilisateur
    - Redirection based on keyword : Analyse des réponses
    - Options de réponse :
        - **OUI** : Utilisateur prêt
        - **pas reçu** : Problème de réception
        - **patience** : Demande d'attente
        - **code** : Utilisateur a déjà le code
        - **Other** : Autre situation

## 4. Entrée du code PIN
- **Set variable [CODEPIN]** : Enregistre le code fourni par l'utilisateur
- **bon code pin ?** : Vérification de la validité du code
    - **Vrai** : Succès de l'authentification
    - **Faux** : Échec, redirection

## 5. Redirections post-vérification
- **Redirection en [TAG]** : Basée sur des mots-clés spécifiques
    - Options de réponse :
        - **oui** : Confirmation
        - **non** : Refus
        - **Other** : Autre situation
- **end** : Fin du processus
    - Rappeler-nous quand vous serez [...] : Message de conclusion

## 6. Redirection SUJET
**Redirection en [SUJET]** : Classification par sujet

- **8 prélèvis** : Gestion des prélèvements automatiques
- **14 contrat** : Questions liées aux contrats
- **12 17 payer** : Options de paiement
- **10 vidage box** : Maintenance technique
- **Other** : Autres sujets

## 7. Gestion des sujets
- **gestion prélèvis** : Module de gestion des prélèvements
- **contrat** : Gestion des contrats
- **payer2** : Options de paiement
- **Vidage box** : Fonctionnalité technique