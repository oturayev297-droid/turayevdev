import json
import re
import threading
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Experience, Project, AIOrder
from .forms import ContactForm
from .ai_service import GeminiAssistant


def send_telegram_async(bot_token, chat_id, text, parse_mode='HTML'):
    """Sends a Telegram message asynchronously in a background thread with a timeout."""
    def _send():
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            requests.post(url, data={
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }, timeout=5)
        except requests.RequestException:
            pass

    threading.Thread(target=_send, daemon=True).start()


def home(request):
    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects})


def resume(request):
    experiences = Experience.objects.all().order_by('-start_date')
    skills = [
        'Python', 'Django', 'JavaScript', 'HTML/CSS', 
        'Modern UI/UX', 'Git'
    ]
    return render(request, 'resume.html', {'experiences': experiences, 'skills': skills})


def projects(request):
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})


@require_POST
def contact_view(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        msg = form.save()
        
        # Telegram Notification
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        if bot_token and chat_id:
            text = (
                f"🚀 <b>Yangi Xabar!</b>\n\n"
                f"👤 <b>Kimdan:</b> {msg.full_name}\n"
                f"✈️ <b>Telegram:</b> {msg.telegram}\n"
                f"📝 <b>Mavzu:</b> {msg.subject}\n\n"
                f"💬 <b>Xabar:</b>\n{msg.message}"
            )
            send_telegram_async(bot_token, chat_id, text, parse_mode='HTML')
                
        return JsonResponse({
            'status': 'success', 
            'message': 'Xabaringiz muvaffaqiyatli yuborildi!'
        })
    
    return JsonResponse({
        'status': 'error', 
        'errors': form.errors, 
        'message': 'Qatorlar to\'g\'ri to\'ldirilmagan.'
    }, status=400)


@require_POST
def ai_chat_handler(request):
    print(f"DEBUG: ai_chat_handler hit. Method: {request.method}")
    try:
        data = json.loads(request.body)
        msg = data.get('message', '')
        history = data.get('history', [])
        print(f"DEBUG: Message received: {msg[:20]}...")
        
        assistant = GeminiAssistant()
        response_text, finalized = assistant.chat(msg, history=history)
        print(f"DEBUG: Assistant responded. Finalized: {finalized}")
        
        # Clean up response text if it contains the metadata tag
        clean_response = re.sub(r"###LEAD_DATA=.*###", "", response_text).strip()
        
        if finalized:
            match = re.search(r"###LEAD_DATA=(.*)###", response_text)
            if match:
                try:
                    lead_data = json.loads(match.group(1))
                    # Save to Database
                    order = AIOrder.objects.create(
                        client_name=lead_data.get('name', 'Noma\'lum'),
                        project_brief=lead_data.get('brief', msg),
                        estimated_price="Kelishiladi ($)",
                        chat_transcript=(
                            f"Last Message: {msg}\n"
                            f"Full AI Response: {response_text}"
                        )
                    )
                    
                    # Notify Ozodbek via Telegram (SMS-like)
                    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
                    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
                    if bot_token and chat_id:
                        text = (
                            f"🔥 *YANGI ZAKAZ (AI)*\n\n"
                            f"👤 *Mijoz:* {order.client_name}\n"
                            f"📁 *Loyiha:* {order.project_brief}\n\n"
                            f"🤖 _Gemini AI orqali suhbat yakunlandi._"
                        )
                        send_telegram_async(bot_token, chat_id, text, parse_mode='Markdown')
                except Exception:
                    pass

        return JsonResponse({'response': clean_response, 'finalized': finalized})
    except Exception as gl_e:
        return JsonResponse({
            'response': f"Texnik xato: {str(gl_e)}", 
            'finalized': False
        }, status=500)


