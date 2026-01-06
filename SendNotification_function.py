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
