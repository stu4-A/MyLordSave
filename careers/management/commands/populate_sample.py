from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from careers.models import CareerOpportunity, StudentProfile
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate sample career opportunities and a demo user'
    def handle(self, *args, **options):
        CareerOpportunity.objects.all().delete()
        today = date.today()
        samples = [
            ('Acme Corp','Software Engineer','Work on backend APIs','https://acme.example.com/apply', today + timedelta(days=30)),
            ('BetaTech','Data Analyst','Data pipelines and visualization','https://beta.example.com/apply', today + timedelta(days=15)),
            ('GreenEnergy','Embedded Systems Intern','Firmware for IoT sensors','https://green.example.com/apply', today + timedelta(days=45)),
            ('FinX','DevOps Engineer','CI/CD and cloud infra','https://finx.example.com/apply', today + timedelta(days=20)),
        ]
        for c,r,dsc,link,dl in samples:
            CareerOpportunity.objects.create(company=c, role=r, description=dsc, link=link, deadline=dl)
        # create demo admin/user
        if not User.objects.filter(username='student1').exists():
            u = User.objects.create_user('student1','student1@example.com','password123')
            sp = StudentProfile.objects.create(user=u, skills='Python,SQL,Git', enrolled_subjects='Databases,Operating Systems')
        self.stdout.write('Sample data created. Username: student1 Password: password123')
