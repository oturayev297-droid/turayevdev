import os
import django
import sys

# Add project root to path
sys.path.append('c:/Users/user/Desktop/portfolio')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from portal.models import Project

def seed_projects():
    # Clear existing projects
    Project.objects.all().delete()
    
    projects_data = [
        {
            "title": "Upgrade Tech Store",
            "category": "E-Commerce",
            "description": "Yuqori unumdorlikka ega kompyuter va gaming jihozlari uchun ixtisoslashgan onlayn do'kon.",
            "image": "Снимок экрана 2026-02-12 093740.png"
        },
        {
            "title": "Anor Travel",
            "category": "Tourism",
            "description": "O'zbekiston va Markaziy Osiyo bo'ylab premium turistik xizmatlar ko'rsatish platformasi.",
            "image": "Снимок экрана 2026-02-12 095756.png"
        },
        {
            "title": "IT Academy Catalog",
            "category": "Ed-Tech",
            "description": "Professional dasturlash kurslarini boshqaruvchi va sotuvchi murakkab LMS tizimi.",
            "image": "Снимок экрана 2026-02-12 094807.png"
        },
        {
            "title": "Restaurantly",
            "category": "Gastronomy",
            "description": "Hashamatli restoranlar uchun onlayn menyu va stol band qilish (booking) tizimi.",
            "image": "Снимок экрана 2026-02-12 093047.png"
        },
        {
            "title": "HomeSpace",
            "category": "Real Estate",
            "description": "Ko'chmas mulkni ijaraga berish va sotish bo'yicha zamonaviy qidiruv portali.",
            "image": "Снимок экрана 2026-02-12 093614.png"
        },
        {
            "title": "Learner Platform",
            "category": "Education",
            "description": "Onlayn kurslar va masofaviy ta'limni tashkil etuvchi zamonaviy veb-platforma.",
            "image": "Снимок экрана 2026-02-12 093401.png"
        },
        {
            "title": "Durdona Ceremony",
            "category": "Events",
            "description": "Tantanalar saroyi va premium restoranlar uchun mo'ljallangan bron qilish sayti.",
            "image": "Снимок экрана 2026-02-12 095022.png"
        },
        {
            "title": "MultiShop Store",
            "category": "Retail",
            "description": "Turli xildagi tovarlar savdosi uchun mo'ljallangan universal e-commerce yechimi.",
            "image": "Снимок экрана 2026-02-12 100105.png"
        }
    ]
    
    for p in projects_data:
        Project.objects.create(
            title=p['title'],
            category=p['category'],
            description=p['description'],
            image_path=f"image/{p['image']}",
            tech_stack="Django, Python, CSS3, GSAP",
            link="#"
        )
    print(f"Successfully seeded {len(projects_data)} projects.")

if __name__ == "__main__":
    seed_projects()
