from google import genai
import json
from django.conf import settings

class GeminiAssistant:
    def __init__(self):
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if api_key:
            self.client = genai.Client(api_key=api_key)
            # Targeting 2.5-flash which is available in this 2026 environment
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None

    def get_system_prompt(self):
        return """
        Siz Ozodbek Turayevning (Portfolio egasi) shaxsiy virtual yordamchisiz. 
        Ozodbek haqida: Buxorolik, 2020-yildan beri IT-da, Middle darajadagi mutaxassis. 
        AI jamoasi bilan Python/Django, iOS va Android (AI bilan integratsiyalashgan) loyihalar yaratadi.
        
        Sizning vazifalaringiz:
        1. Mijozlar bilan xushmuomala Ozodbek nomidan gaplashish.
        2. Ularning loyiha g'oyalari bo'yicha maslahat berish (siz kabi aqllisiz, IT bo'yicha barcha savollarga javob bering).
        3. Standart narxlar haqida ma'lumot berish:
           - Landing Page: 500$ - 1500$
           - E-commerce: 2000$ - 5000$
           - Mobile App: 3000$+
        4. Agar mijoz loyiha zakaz qilmoqchi bo'lsa, uning ismi va loyiha haqida qisqacha ma'lumotni oling.
        
        MUHIM: Suhbat yakunida mijoz ismi va loyiha haqida aniq ma'lumotga ega bo'lsangiz, xabar oxirida manavi maxsus formatda LEAD ma'lumotlarini qoldiring:
        ###LEAD_DATA={"name": "Mijoz ismi", "brief": "loyiha tavsifi", "finalized": true}###
        
        Tilllar: O'zbek, Rus, Ingliz. Qaysi tilda murojaat qilishsa, o'sha tilda javob bering.
        """

    def chat(self, user_message, history=[]):
        if not self.client:
            return "Hozircha AI tizimi sozlanmagan. Iltimos, API key qo'shing.", False

        # Convert simple history to GenAI format
        contents = []
        for h in history:
            contents.append({
                "role": h['role'],
                "parts": [{"text": h['content']}]
            })
        
        # Add current message
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={"system_instruction": self.get_system_prompt()}
            )
            text = response.text
            finalized = "###LEAD_DATA=" in text
            return text, finalized
        except Exception as e:
            return f"Xatolik yuz berdi: {str(e)}", False
