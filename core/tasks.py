import time
from celery import shared_task
from django.utils import timezone
from .models import ProcessedMessage


@shared_task(bind=True)
def process_message(self, message):
    task_id = self.request.id
    
    # Create or update database record
    try:
        processed_msg, created = ProcessedMessage.objects.get_or_create(
            task_id=task_id,
            defaults={
                'original_message': message,
                'status': 'processing'
            }
        )
        if not created:
            processed_msg.status = 'processing'
            processed_msg.save()
        
        print(f'Processing message: {message} (Task ID: {task_id})')
        time.sleep(3)
        
        # Update status to completed
        processed_msg.status = 'completed'
        processed_msg.processed_at = timezone.now()
        processed_msg.save()
        
        print(f'Message processed: {message}')
        return {
            'type': 'message_processed',
            'original_message': message,
            'status': 'completed'
        }
    
    except Exception as e:
        print(f'Error processing message: {e}')
        # Update status to failed
        try:
            processed_msg = ProcessedMessage.objects.get(task_id=task_id)
            processed_msg.status = 'failed'
            processed_msg.processed_at = timezone.now()
            processed_msg.save()
        except ProcessedMessage.DoesNotExist:
            pass
        
        return {
            'type': 'message_processed',
            'original_message': message,
            'status': 'failed'
        }


@shared_task
def heartbeat():
    print('Heartbeat task running...')
    return {
        'type': 'heartbeat',
        'message': "heartbeat successful.",
        'status': 'active'
    }