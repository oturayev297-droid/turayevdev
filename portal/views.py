import json
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Experience, Project, AIOrder
from .forms import ContactForm

def home(request):
    projects = Project.objects.all()
    return render(request, 'home.html', {'projects': projects})

def resume(request):
    experiences = Experience.objects.all().order_by('-start_date')
    skills = ['Python', 'Django', 'JavaScript', 'HTML/CSS', 'Modern UI/UX', 'Git']
    return render(request, 'resume.html', {'experiences': experiences, 'skills': skills})

def projects(request):
    projects = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects})

@require_POST
def contact_view(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        msg = form.save()
        
        # Optional: Telegram Notification
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        
        if bot_token and chat_id:
            text = f"🚀 *Yangi Xabar!*\n\n👤 *Kimdan:* {msg.full_name}\n📧 *Email:* {msg.email}\n📝 *Mavzu:* {msg.subject}\n\n💬 *Xabar:* {msg.message}"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            try:
                requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'})
            except:
                pass
                
        return JsonResponse({'status': 'success', 'message': 'Xabaringiz muvaffaqiyatli yuborildi!'})
    
from .ai_service import GeminiAssistant
import re

@require_POST
def ai_chat_handler(request):
    try:
        data = json.loads(request.body)
        msg = data.get('message', '')
        history = data.get('history', [])
        
        assistant = GeminiAssistant()
        response_text, finalized = assistant.chat(msg, history=history)
        
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
                        chat_transcript=f"Last Message: {msg}\nFull AI Response: {response_text}"
                    )
                    
                    # Notify Ozodbek via Telegram (SMS-like)
                    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
                    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
                    if bot_token and chat_id:
                        text = f"🔥 *YANGI ZAKAZ (AI)*\n\n👤 *Mijoz:* {order.client_name}\n📁 *Loyiha:* {order.project_brief}\n\n🤖 _Gemini AI orqali suhbat yakunlandi._"
                        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        requests.post(url, data={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'})
                except Exception as e:
                    pass

        return JsonResponse({'response': clean_response, 'finalized': finalized})
    except Exception as gl_e:
        return JsonResponse({'response': f"Texnik xato: {str(gl_e)}", 'finalized': False}, status=500)
