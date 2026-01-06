# aws-serverless-order-processing
# 🛒 Système de Traitement de Commandes Asynchrones sur AWS

![AWS](https://img.shields.io/badge/AWS-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Une architecture serverless complète pour le traitement asynchrone de commandes e-commerce utilisant les services AWS.

## 📋 Table des matières

- [Vue d'ensemble](#-vue-densemble)
- [Architecture](#-architecture)
- [Services AWS utilisés](#-services-aws-utilisés)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Structure du projet](#-structure-du-projet)
- [Configuration](#-configuration)
- [Déploiement](#-déploiement)
- [Tests](#-tests)
- [Monitoring](#-monitoring)
- [Dépannage](#-dépannage)
- [Coûts estimés](#-coûts-estimés)
- [Contributeurs](#-contributeurs)
- [Licence](#-licence)

## 🎯 Vue d'ensemble

Ce projet implémente un système de traitement de commandes e-commerce avec :
- ✅ Interface web responsive
- ✅ Traitement asynchrone via file de messages
- ✅ Orchestration de workflow avec Step Functions
- ✅ Architecture 100% serverless
- ✅ Scalabilité automatique

**Durée d'implémentation** : ~45 minutes

## 🏗️ Architecture

![Architecture Serverless](https://raw.githubusercontent.com/votre-username/votre-repo/main/docs/architecture.png)

### Flux de traitement

1. **Frontend** : L'utilisateur soumet une commande via l'interface web
2. **Application Flask** : Reçoit la commande et l'envoie à SQS
3. **Amazon SQS** : Stocke le message dans la file d'attente
4. **Step Functions** : Orchestre le workflow de traitement
5. **Lambda Functions** : Exécutent la logique métier en 3 étapes :
   - **Validation** : Vérifie la validité de la commande
   - **Paiement** : Traite le paiement (simulation)
   - **Notification** : Envoie une notification de confirmation

### Diagramme d'architecture

```
┌─────────────┐
│ Utilisateur │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Application Web     │
│  Elastic Beanstalk   │
│  (Flask + Python)    │
└──────┬───────────┬───┘
       │           │
       ▼           ▼
┌────────────┐  ┌─────────────────┐
│ Amazon SQS │  │ Step Functions  │
│ Queue      │  │ State Machine   │
└────────────┘  └────────┬────────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌─────────┐ ┌──────────┐ ┌──────────┐
         │Validate │ │ Process  │ │   Send   │
         │ Order   │ │ Payment  │ │Notification│
         │ Lambda  │ │  Lambda  │ │  Lambda  │
         └─────────┘ └──────────┘ └──────────┘
```

## 🔧 Services AWS utilisés

| Service | Rôle | Coût estimé/mois |
|---------|------|------------------|
| **AWS Elastic Beanstalk** | Hébergement de l'application web | ~$15 |
| **Amazon SQS** | File de messages asynchrone | ~$0.40 |
| **AWS Step Functions** | Orchestration du workflow | ~$0.025 |
| **AWS Lambda** | Traitement métier serverless | ~$0.20 |
| **IAM** | Gestion des permissions | Gratuit |

**Total estimé** : ~$16/mois (avec Free Tier)

## 📦 Prérequis

- Compte AWS actif
- AWS CLI configuré (optionnel)
- Python 3.11+
- Accès à la console AWS

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/order-processing-aws.git
cd order-processing-aws
```

### 2. Créer la file SQS

```bash
# Via AWS CLI
aws sqs create-queue --queue-name orders-queue --region us-east-1
```

Ou via la console AWS : **SQS** → **Create queue**

### 3. Créer les fonctions Lambda

Déployez les 3 fonctions Lambda depuis le dossier `lambda/` :
- `ValidateOrder`
- `ProcessPayment`
- `SendNotification`

### 4. Créer la Step Function

Utilisez la définition dans `step-functions/workflow.json`

### 5. Configurer les permissions IAM

Attachez les policies suivantes au rôle `aws-elasticbeanstalk-ec2-role` :
- `AmazonSQSFullAccess`
- `AWSStepFunctionsFullAccess`

## 📁 Structure du projet

```
order-processing-aws/
├── application.py              # Application Flask principale
├── requirements.txt            # Dépendances Python
├── templates/
│   └── index.html             # Interface web
├── lambda/
│   ├── validate_order.py      # Lambda validation
│   ├── process_payment.py     # Lambda paiement
│   └── send_notification.py   # Lambda notification
├── step-functions/
│   └── workflow.json          # Définition Step Functions
├── docs/
│   ├── architecture.png       # Diagramme d'architecture
│   └── documentation.md       # Documentation détaillée
├── .gitignore
├── LICENSE
└── README.md
```

## ⚙️ Configuration

### Variables d'environnement

Modifiez `application.py` avec vos valeurs :

```python
# Configuration AWS
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/YOUR-ACCOUNT/orders-queue'
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:YOUR-ACCOUNT:stateMachine:OrderProcessingWorkflow'
```

### Créer le package de déploiement

```bash
cd order-processing-aws
zip -r order-app.zip application.py requirements.txt templates/
```

## 🚢 Déploiement

### Option 1 : Via la console AWS (recommandé)

1. Accédez à **AWS Elastic Beanstalk**
2. **Create application** :
   - Name : `order-processing-app`
   - Platform : Python 3.11
3. **Upload and deploy** : `order-app.zip`
4. Attendez 5-7 minutes

### Option 2 : Via AWS CLI

```bash
# Initialiser l'application
eb init -p python-3.11 order-processing-app --region us-east-1

# Créer l'environnement
eb create order-processing-env

# Déployer
eb deploy
```

### Vérification du déploiement

```bash
# Obtenir l'URL de l'application
eb status

# Ouvrir dans le navigateur
eb open
```

## 🧪 Tests

### Test de l'interface web

1. Accédez à l'URL de votre application
2. Remplissez le formulaire :
   - **Customer Name** : John Doe
   - **Product** : Laptop
   - **Amount** : 1500
3. Soumettez la commande
4. Vérifiez le message de succès

### Test du workflow Step Functions

```bash
# Via AWS CLI
aws stepfunctions start-execution \
    --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:OrderProcessingWorkflow \
    --input '{"order":{"orderId":"test-123","amount":100}}'
```

### Vérification des messages SQS

```bash
# Récupérer les messages
aws sqs receive-message \
    --queue-url https://sqs.us-east-1.amazonaws.com/ACCOUNT/orders-queue
```

## 📊 Monitoring

### Logs de l'application

```bash
# Via Elastic Beanstalk CLI
eb logs

# Ou via la console
Elastic Beanstalk → Environment → Logs → Request Logs
```

### Métriques CloudWatch

- **Lambda** : Invocations, Duration, Errors
- **SQS** : Messages sent, Messages received
- **Step Functions** : Executions started, Succeeded, Failed

### Dashboard CloudWatch (optionnel)

Créez un dashboard personnalisé pour suivre :
- Nombre de commandes/heure
- Taux de succès des paiements
- Latence moyenne de traitement

## 🔍 Dépannage

### Erreur : "Environment health Degraded"

**Solution** :
```bash
# Vérifier les logs
eb logs

# Redéployer
eb deploy
```

### Erreur : "ModuleNotFoundError: No module named 'application'"

**Cause** : Structure du ZIP incorrecte

**Solution** : Les fichiers doivent être à la racine du ZIP, pas dans un sous-dossier

```bash
# Correct
zip -r app.zip application.py requirements.txt templates/

# Incorrect
zip -r app.zip ./order-processing-aws/*
```

### Erreur : "Access Denied" (SQS/Step Functions)

**Solution** : Vérifier les permissions IAM

```bash
# Lister les policies du rôle
aws iam list-attached-role-policies --role-name aws-elasticbeanstalk-ec2-role
```

### Erreur 502 Bad Gateway

**Solutions** :
1. Vérifier que le port est `8000` (pas `8080`)
2. Vérifier que Flask démarre correctement dans les logs
3. Vérifier les security groups

## 💰 Coûts estimés

### Free Tier (12 premiers mois)
- Elastic Beanstalk : 750h/mois gratuites (t2.micro)
- Lambda : 1M requêtes/mois gratuites
- Step Functions : 4000 transitions/mois gratuites
- SQS : 1M requêtes/mois gratuites

### Après Free Tier
| Ressource | Usage mensuel | Coût estimé |
|-----------|---------------|-------------|
| EC2 (t2.micro) | 730h | $8.47 |
| Lambda | 10,000 invocations | $0.20 |
| Step Functions | 5,000 transitions | $0.125 |
| SQS | 50,000 messages | $0.02 |
| Data Transfer | 10 GB | $0.90 |
| **Total** | | **~$9.72/mois** |

## 🧹 Nettoyage des ressources

```bash
# Via CLI
eb terminate order-processing-env

# Supprimer les autres ressources
aws sqs delete-queue --queue-url YOUR_QUEUE_URL
aws stepfunctions delete-state-machine --state-machine-arn YOUR_STATE_MACHINE_ARN
aws lambda delete-function --function-name ValidateOrder
aws lambda delete-function --function-name ProcessPayment
aws lambda delete-function --function-name SendNotification
```

## 🤝 Contributeurs

- Votre Nom - [@lahda](https://github.com/lahda)

## 🔗 Ressources

- [Documentation AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Documentation Amazon SQS](https://docs.aws.amazon.com/sqs/)
- [Documentation AWS Step Functions](https://docs.aws.amazon.com/step-functions/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)

## 📮 Support

Pour toute question ou problème :
- Ouvrez une [issue](https://github.com/votre-username/order-processing-aws/issues)


---

⭐ **Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile !**

**Créé avec ❤️ pour apprendre AWS**
