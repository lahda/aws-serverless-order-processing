import json
import random
import time

def lambda_handler(event, context):
    order_id = event.get('orderId', 'unknown')
    amount = event.get('amount', 0)
    
    # Simulation du traitement
    time.sleep(2)
    
    # 90% de succès
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