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
