# 🛒 Système de Traitement de Commandes AWS

## 📋 Vue d'ensemble du projet

Ce projet implémente un système de traitement asynchrone de commandes e-commerce utilisant les services AWS suivants :
- **AWS Elastic Beanstalk** : Hébergement de l'application web
- **Amazon SQS** : File d'attente de messages
- **AWS Step Functions** : Orchestration du workflow
- **AWS Lambda** : Traitement métier (3 fonctions)

**Durée d'implémentation** : ~45 minutes

---

## 🏗️ Architecture

```
┌─────────────┐
│  Utilisateur │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│   Application Web (Flask)   │
│   AWS Elastic Beanstalk     │
└──────┬──────────────┬───────┘
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────────┐
│ Amazon SQS  │  │ AWS Step Functions│
│orders-queue │  │OrderProcessing    │
└─────────────┘  └────────┬─────────┘
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
          ┌─────────┐ ┌─────────┐ ┌──────────┐
          │Validate │ │Process  │ │Send      │
          │Order    │ │Payment  │ │Notification│
          │Lambda   │ │Lambda   │ │Lambda    │
          └─────────┘ └─────────┘ └──────────┘
```

---

## 🚀 Guide d'implémentation pas à pas

### Prérequis
- Compte AWS actif
- Accès à la console AWS
- Éditeur de texte

---

## ÉTAPE 1 : Créer la file SQS (5 min)

### Actions
1. Accédez à **Amazon SQS** dans la console AWS
2. Cliquez sur **"Create queue"**

### Configuration
- **Type** : Standard
- **Name** : `orders-queue`
- **Visibility timeout** : 30 seconds
- Autres paramètres : valeurs par défaut

### Résultat
- Notez l'URL de la queue : `https://sqs.us-east-1.amazonaws.com/[ACCOUNT-ID]/orders-queue`

---

## ÉTAPE 2 : Créer les fonctions Lambda (15 min)

### Lambda 1 : ValidateOrder

**Configuration**
- **Function name** : `ValidateOrder`
- **Runtime** : Python 3.12
- **Architecture** : x86_64

**Code source**
```python
import json
import random

def lambda_handler(event, context):
    order = event.get('order', {})
    order_id = order.get('orderId', 'unknown')
    amount = order.get('amount', 0)
    
    # Validation simple
    if amount > 0 and amount < 10000:
        return {
            'statusCode': 200,
            'orderId': order_id,
            'amount': amount,
            'isValid': True,
            'message': 'Order validated successfully'
        }
    else:
        return {
            'statusCode': 400,
            'orderId': order_id,
            'isValid': False,
            'message': 'Invalid order amount'
        }
```

**Note** : Copiez l'ARN de la fonction pour Step Functions

---

### Lambda 2 : ProcessPayment

**Configuration**
- **Function name** : `ProcessPayment`
- **Runtime** : Python 3.12
- **Architecture** : x86_64

**Code source**
```python
import json
import random
import time

def lambda_handler(event, context):
    order_id = event.get('orderId', 'unknown')
    amount = event.get('amount', 0)
    
    # Simulation du traitement (2 secondes)
    time.sleep(2)
    
    # 90% de taux de succès
    success = random.random() > 0.1
    
    if success:
        return {
            'statusCode': 200,
            'orderId': order_id,
            'amount': amount,
            'paymentStatus': 'SUCCESS',
            'transactionId': f'TXN-{random.randint(10000, 99999)}',
            'message': 'Payment processed successfully'
        }
    else:
        return {
            'statusCode': 500,
            'orderId': order_id,
            'paymentStatus': 'FAILED',
            'message': 'Payment processing failed'
        }
```

**Note** : Copiez l'ARN de la fonction pour Step Functions

---

### Lambda 3 : SendNotification

**Configuration**
- **Function name** : `SendNotification`
- **Runtime** : Python 3.12
- **Architecture** : x86_64

**Code source**
```python
import json

def lambda_handler(event, context):
    order_id = event.get('orderId', 'unknown')
    payment_status = event.get('paymentStatus', 'UNKNOWN')
    
    # Simulation d'envoi de notification
    notification_message = f"Order {order_id} - Payment {payment_status}"
    
    return {
        'statusCode': 200,
        'orderId': order_id,
        'notificationSent': True,
        'message': notification_message
    }
```

**Note** : Copiez l'ARN de la fonction pour Step Functions

---

## ÉTAPE 3 : Créer la Step Function (10 min)

### Configuration
1. Accédez à **AWS Step Functions**
2. Cliquez sur **"Create state machine"**
3. Choisissez **"Write your workflow in code"**

### Paramètres
- **Type** : Standard
- **Name** : `OrderProcessingWorkflow`

### Définition du workflow

```json
{
  "Comment": "Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:REGION:ACCOUNT:function:ValidateOrder",
        "Payload": {
          "order.$": "$.order"
        }
      },
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "ResultPath": "$.validationResult",
      "Next": "CheckValidation"
    },
    "CheckValidation": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.validationResult.result.isValid",
          "BooleanEquals": true,
          "Next": "ProcessPayment"
        }
      ],
      "Default": "ValidationFailed"
    },
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:REGION:ACCOUNT:function:ProcessPayment",
        "Payload": {
          "orderId.$": "$.validationResult.result.orderId",
          "amount.$": "$.validationResult.result.amount"
        }
      },
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "ResultPath": "$.paymentResult",
      "Next": "SendNotification"
    },
    "SendNotification": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "arn:aws:lambda:REGION:ACCOUNT:function:SendNotification",
        "Payload": {
          "orderId.$": "$.paymentResult.result.orderId",
          "paymentStatus.$": "$.paymentResult.result.paymentStatus"
        }
      },
      "ResultSelector": {
        "result.$": "$.Payload"
      },
      "ResultPath": "$.notificationResult",
      "End": true
    },
    "ValidationFailed": {
      "Type": "Fail",
      "Error": "ValidationError",
      "Cause": "Order validation failed"
    }
  }
}
```

**⚠️ Important** : Remplacez `REGION` et `ACCOUNT` par vos vraies valeurs, et utilisez les ARN complets de vos fonctions Lambda.

### Résultat
- Notez l'ARN de la state machine : `arn:aws:states:REGION:ACCOUNT:stateMachine:OrderProcessingWorkflow`

---

## ÉTAPE 4 : Créer l'application Elastic Beanstalk (15 min)

### 4.1 Créer l'environnement

1. Accédez à **AWS Elastic Beanstalk**
2. Cliquez sur **"Create application"**

**Configuration**
- **Application name** : `order-processing-app`
- **Platform** : Python
- **Platform branch** : Python 3.11
- **Application code** : Sample application (temporairement)

3. Cliquez sur **"Create application"** (attendre 5-7 minutes)

---

### 4.2 Structure du projet local

Créez un dossier `ORDER-APP` avec cette structure :

```
ORDER-APP/
├── application.py
├── requirements.txt
├── Procfile
└── templates/
    └── index.html
```

---

### 4.3 Fichier application.py

```python
from flask import Flask, render_template, request, jsonify
import boto3
import json
import uuid
from datetime import datetime

application = Flask(__name__)

# Clients AWS
sqs = boto3.client('sqs', region_name='us-east-1')
stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')

# Configuration - À REMPLACER avec vos valeurs
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/ACCOUNT-ID/orders-queue'
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:ACCOUNT-ID:stateMachine:OrderProcessingWorkflow'

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        data = request.json
        order_id = str(uuid.uuid4())[:8]
        
        order = {
            'orderId': order_id,
            'customerName': data.get('customerName'),
            'product': data.get('product'),
            'amount': float(data.get('amount')),
            'timestamp': datetime.now().isoformat()
        }
        
        # Envoyer à SQS
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order)
        )
        
        # Démarrer Step Function
        stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({'order': order})
        )
        
        return jsonify({
            'success': True,
            'orderId': order_id,
            'message': 'Order submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@application.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8000)
```

---

### 4.4 Fichier requirements.txt

```
flask==3.0.0
boto3==1.34.0
```

---

### 4.5 Fichier templates/index.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>Order Processing System</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #FF9900;
            text-align: center;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #FF9900;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #EC7211;
        }
        .message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 Order Processing System</h1>
        <form id="orderForm">
            <div class="form-group">
                <label>Customer Name:</label>
                <input type="text" id="customerName" required>
            </div>
            <div class="form-group">
                <label>Product:</label>
                <input type="text" id="product" required>
            </div>
            <div class="form-group">
                <label>Amount ($):</label>
                <input type="number" id="amount" step="0.01" required>
            </div>
            <button type="submit">Submit Order</button>
        </form>
        <div id="message" class="message"></div>
    </div>

    <script>
        document.getElementById('orderForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                customerName: document.getElementById('customerName').value,
                product: document.getElementById('product').value,
                amount: document.getElementById('amount').value
            };
            
            try {
                const response = await fetch('/submit-order', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                const messageDiv = document.getElementById('message');
                
                if (result.success) {
                    messageDiv.className = 'message success';
                    messageDiv.textContent = `✓ Order ${result.orderId} submitted successfully!`;
                    document.getElementById('orderForm').reset();
                } else {
                    messageDiv.className = 'message error';
                    messageDiv.textContent = `✗ Error: ${result.error}`;
                }
                
                messageDiv.style.display = 'block';
                setTimeout(() => {
                    messageDiv.style.display = 'none';
                }, 5000);
                
            } catch (error) {
                alert('Error submitting order: ' + error);
            }
        });
    </script>
</body>
</html>
```

---

### 4.6 Créer le fichier ZIP

**Méthode PowerShell (recommandée)**
```powershell
cd ORDER-APP
Compress-Archive -Path application.py,requirements.txt,templates -DestinationPath ..\order-app.zip -Force
```

**Structure du ZIP**
```
order-app.zip
├── application.py          ← directement à la racine
├── requirements.txt        ← directement à la racine
└── templates/              ← directement à la racine
    └── index.html
```

---

### 4.7 Configurer les permissions IAM

1. Accédez à **IAM** → **Roles**
2. Cherchez `aws-elasticbeanstalk-ec2-role`
3. Cliquez sur **"Add permissions"** → **"Attach policies"**
4. Ajoutez ces policies :
   - ✅ `AmazonSQSFullAccess`
   - ✅ `AWSStepFunctionsFullAccess`

---

### 4.8 Déployer l'application

1. Retournez sur **Elastic Beanstalk** → Votre environnement
2. Cliquez sur **"Upload and deploy"**
3. Sélectionnez `order-app.zip`
4. Cliquez sur **"Deploy"**
5. Attendez 3-5 minutes

---

## ÉTAPE 5 : Test du système (5 min)

### Test de l'application web

1. Cliquez sur l'URL de votre environnement Elastic Beanstalk
2. Remplissez le formulaire :
   - **Customer Name** : John Doe
   - **Product** : Laptop
   - **Amount** : 1500
3. Cliquez sur **"Submit Order"**
4. Vous devriez voir un message de succès avec l'ID de commande

### Vérification dans Step Functions

1. Accédez à **AWS Step Functions**
2. Cliquez sur `OrderProcessingWorkflow`
3. Vous devriez voir une nouvelle exécution
4. Cliquez dessus pour voir le workflow visuel avec chaque étape

### Vérification dans SQS

1. Accédez à **Amazon SQS**
2. Cliquez sur `orders-queue`
3. Cliquez sur **"Send and receive messages"**
4. Cliquez sur **"Poll for messages"**
5. Vous devriez voir vos messages de commandes

---

## 🔧 Dépannage

### Erreur : Environment health Degraded

**Cause** : Structure du ZIP incorrecte ou module non trouvé

**Solution** :
- Vérifiez que les fichiers sont directement à la racine du ZIP
- Pas de dossier parent dans le ZIP

### Erreur : ModuleNotFoundError

**Solution** :
- Vérifiez que `requirements.txt` contient flask et boto3
- Re-déployez l'application

### Erreur : Access Denied (SQS ou Step Functions)

**Solution** :
- Vérifiez les permissions IAM du rôle `aws-elasticbeanstalk-ec2-role`
- Ajoutez les policies manquantes

### Erreur 502 Bad Gateway

**Solution** :
- Vérifiez les logs : Elastic Beanstalk → Logs → Request Logs
- Vérifiez que le port est 8000 (pas 8080)

---

## 📊 Monitoring et Logs

### Logs Elastic Beanstalk
- Console → Elastic Beanstalk → Logs → "Request Logs"
- Fichiers importants :
  - `/var/log/web.stdout.log` : Logs de l'application
  - `/var/log/eb-engine.log` : Logs de déploiement

### Logs Lambda
- Console → Lambda → Fonction → Monitor → View logs in CloudWatch

### Exécutions Step Functions
- Console → Step Functions → State machine → Executions
- Visualisation graphique du workflow

---

## 💰 Estimation des coûts (usage modéré)

| Service | Coût estimé/mois |
|---------|------------------|
| Elastic Beanstalk (t2.micro) | ~$15 |
| Lambda (1000 exécutions) | ~$0.20 |
| Step Functions (1000 transitions) | ~$0.025 |
| SQS (1000 messages) | ~$0.40 |
| **Total** | **~$16/mois** |

**Note** : Utilisez le Free Tier AWS pour réduire les coûts.

---

## 🧹 Nettoyage des ressources

Pour éviter des frais inutiles, supprimez les ressources :

1. **Elastic Beanstalk** : Terminate environment
2. **Lambda** : Delete functions (ValidateOrder, ProcessPayment, SendNotification)
3. **Step Functions** : Delete state machine
4. **SQS** : Delete queue
5. **IAM** : Optionnel - Détacher les policies ajoutées

---

## 📝 Points clés d'apprentissage

✅ Déploiement d'applications avec Elastic Beanstalk  
✅ Utilisation de files de messages avec SQS  
✅ Orchestration de workflows avec Step Functions  
✅ Intégration de fonctions Lambda  
✅ Configuration de permissions IAM  
✅ Architecture microservices sur AWS  

---

## 🔗 Ressources supplémentaires

- [Documentation AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Documentation Amazon SQS](https://docs.aws.amazon.com/sqs/)
- [Documentation AWS Step Functions](https://docs.aws.amazon.com/step-functions/)
- [Documentation AWS Lambda](https://docs.aws.amazon.com/lambda/)

---

## Informations du projet

**Durée** : 45 minutes  
**Niveau** : Intermédiaire  
**Services AWS** : 4 (Elastic Beanstalk, SQS, Step Functions, Lambda)  
**Langage** : Python 3.12  
**Framework** : Flask 3.0.0  

---

**Date de création** : Janvier 2026  
**Version** : 1.0