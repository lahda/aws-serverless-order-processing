from flask import Flask, render_template, request, jsonify
import boto3
import json
import uuid
from datetime import datetime

application = Flask(__name__)

# Clients AWS
sqs = boto3.client('sqs', region_name='us-east-1')  # Change la région
stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')

# Configuration (à remplacer avec tes valeurs)
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/381492097033/orders-queue'
STATE_MACHINE_ARN = 'arn:aws:states:us-east-1:381492097033:stateMachine:OrderProcessingWorkflow'

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

# if __name__ == '__main__':
#     application.run(host='0.0.0.0', port=8000)
