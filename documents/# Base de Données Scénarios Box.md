# Base de Données Scénarios Box

## Sites
| site_id | ville | adresse | code_postal | nombre_box | box_disponibles |
|---------|--------|----------|-------------|------------|-----------------|
| MP001 | Montpellier | 123 Avenue de la Liberté | 34000 | 100 | 15 |
| MP002 | Montpellier | 45 Rue des Arceaux | 34000 | 50 | 8 |
| LY001 | Lyon | 78 Rue de la République | 69002 | 150 | 20 |
| LY002 | Lyon | 156 Avenue Jean Jaurès | 69007 | 80 | 12 |
| MS001 | Marseille | 89 Boulevard des Dames | 13002 | 120 | 18 |
| MS002 | Marseille | 234 Rue du Port | 13002 | 60 | 10 |

## Box
| box_id | site_id | taille | prix_mensuel | statut | type | caracteristiques |
|--------|---------|---------|--------------|---------|------|------------------|
| MP001-01 | MP001 | 3m² | 45€ | occupé | standard | accès 24/7 |
| MP001-02 | MP001 | 5m² | 75€ | disponible | standard | accès 24/7 |
| MP001-03 | MP001 | 10m² | 150€ | occupé | sécurisé | accès 24/7, caméra |
| LY001-01 | LY001 | 3m² | 48€ | occupé | standard | accès 24/7 |
| LY001-02 | LY001 | 5m² | 80€ | disponible | sécurisé | accès 24/7, caméra |
| MS001-01 | MS001 | 3m² | 42€ | occupé | standard | accès 24/7 |

## Clients
| client_id | nom | prenom | email | telephone | type_client | date_inscription |
|-----------|-----|---------|--------|------------|--------------|------------------|
| CL001 | Dupont | Jean | jean.dupont@email.com | 0612345678 | particulier | 2024-01-15 |
| CL002 | Martin | Sophie | sophie.martin@email.com | 0623456789 | professionnel | 2024-02-01 |
| CL003 | Bernard | Pierre | pierre.bernard@email.com | 0634567890 | particulier | 2024-03-10 |
| CL004 | Dubois | Marie | marie.dubois@email.com | 0645678901 | professionnel | 2024-03-15 |

## Contrats
| contrat_id | client_id | box_id | date_debut | date_fin | prix_mensuel | statut | assurance |
|------------|-----------|---------|------------|----------|--------------|---------|-----------|
| CT001 | CL001 | MP001-01 | 2024-01-15 | 2024-07-15 | 45€ | actif | oui |
| CT002 | CL002 | LY001-01 | 2024-02-01 | 2024-08-01 | 48€ | actif | oui |
| CT003 | CL003 | MS001-01 | 2024-03-10 | 2024-09-10 | 42€ | actif | non |
| CT004 | CL004 | MP001-03 | 2024-03-15 | 2024-09-15 | 150€ | actif | oui |

## Paiements
| paiement_id | contrat_id | montant | date_paiement | methode | statut |
|-------------|------------|---------|---------------|---------|---------|
| P001 | CT001 | 45€ | 2024-01-15 | carte | validé |
| P002 | CT001 | 45€ | 2024-02-15 | prélèvement | validé |
| P003 | CT002 | 48€ | 2024-02-01 | virement | validé |
| P004 | CT003 | 42€ | 2024-03-10 | carte | en attente |

## Accès
| acces_id | box_id | client_id | date_acces | type_acces | resultat |
|----------|---------|-----------|------------|------------|-----------|
| A001 | MP001-01 | CL001 | 2024-03-20 14:30 | entrée | succès |
| A002 | MP001-01 | CL001 | 2024-03-20 15:45 | sortie | succès |
| A003 | LY001-01 | CL002 | 2024-03-20 09:15 | entrée | succès |
| A004 | MS001-01 | CL003 | 2024-03-20 11:30 | entrée | échec |

## Incidents
| incident_id | box_id | client_id | date_incident | type_incident | statut | resolution |
|-------------|---------|-----------|---------------|---------------|---------|------------|
| I001 | MP001-01 | CL001 | 2024-03-15 | problème accès | résolu | code réinitialisé |
| I002 | LY001-01 | CL002 | 2024-03-18 | retard paiement | en cours | relance effectuée |
| I003 | MS001-01 | CL003 | 2024-03-20 | dommage | en cours | expertise en cours |

## Relations Clés
- Un site peut avoir plusieurs box (1:N)
- Un box appartient à un seul site (N:1)
- Un client peut avoir plusieurs contrats (1:N)
- Un contrat est lié à un seul box (N:1)
- Un contrat peut avoir plusieurs paiements (1:N)
- Un box peut avoir plusieurs accès (1:N)
- Un box peut avoir plusieurs incidents (1:N)