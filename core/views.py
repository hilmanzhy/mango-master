import json
import time
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult
from .tasks import process_message
from .models import ProcessedMessage


def homepage(request):
    context = {
        'site_title': settings.SITE_TITLE,
    }
    return render(request, 'core/homepage.html', context)


@csrf_exempt
def submit_message(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            process_message.delay(message)
            return JsonResponse({
                'success': True,
                'message': f'Message queued for processing: {message}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please enter a message'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def events(request):
    start_time = float(request.GET.get('start_time', 0))
    
    def event_stream():
        processed_tasks = set()
        while True:
            from app.celery import app
            finished_tasks = []
            
            for task_id in app.backend.client.scan_iter(match="celery-task-meta-*"):
                task_id = task_id.decode().replace("celery-task-meta-", "")
                if task_id not in processed_tasks:
                    result = AsyncResult(task_id)
                    if result.ready():
                        if result.successful():
                            # Get task completion timestamp from result metadata
                            task_info = result.backend.get_task_meta(task_id)
                            task_completion_time = task_info.get('date_done')
                            
                            if task_completion_time:
                                # Parse ISO format timestamp to unix timestamp
                                completion_timestamp = datetime.fromisoformat(task_completion_time.replace('Z', '+00:00')).timestamp()
                                
                                # Only include tasks completed after start_time
                                if completion_timestamp > start_time:
                                    processed_tasks.add(task_id)
                                    finished_tasks.append(result.result)
                            else:
                                # Fallback for tasks without timestamp
                                processed_tasks.add(task_id)
                                finished_tasks.append(result.result)
            
            for result in finished_tasks:
                # Handle different result types
                if isinstance(result, dict):
                    if result.get('type') == 'message_processed':
                        yield f"data: {json.dumps({'type': 'message_processed', 'original_message': result['original_message']})}\n\n"
                    elif result.get('type') == 'heartbeat':
                        yield f"data: {json.dumps({'type': 'heartbeat', 'message': result['message']})}\n\n"
                    else:
                        # Unknown structured result
                        yield f"data: {json.dumps({'type': 'unknown', 'result': result})}\n\n"
                else:
                    # Fallback for non-structured results
                    yield f"data: {json.dumps({'type': 'unknown', 'result': result})}\n\n"
            
            time.sleep(1)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


def history(request):
    from django.core.paginator import Paginator
    
    # Get all processed messages, ordered by most recent first
    messages = ProcessedMessage.objects.all().order_by('-created_at')
    
    # Paginate results (20 messages per page)
    paginator = Paginator(messages, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'site_title': settings.SITE_TITLE,
        'page_obj': page_obj,
    }
    return render(request, 'core/history.html', context)
