from django.core.management.base import BaseCommand
from reference.models import Skill, Profession, Industry


class Command(BaseCommand):
    help = 'Заполняет справочники: навыки, профессии и сферы 4 примерами'

    def handle(self, *args, **kwargs):
        skills = ['Python', 'Django', 'React', 'PostgreSQL']
        professions = [
            'Backend Developer', 'Frontend Developer',
            'Data Scientist', 'DevOps Engineer'
        ]
        industries = ['FinTech', 'E-commerce', 'Healthcare', 'EdTech']

        self.seed_model(Skill, skills)
        self.seed_model(Profession, professions)
        self.seed_model(Industry, industries)

        self.stdout.write(self.style.SUCCESS('Справочники успешно заполнены.'))

    def seed_model(self, model, items):
        for name in items:
            obj, created = model.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f'Создано: {model.__name__} — {name}')
            else:
                self.stdout.write(f'Уже существует: {model.__name__} — {name}')
