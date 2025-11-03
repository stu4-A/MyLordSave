Student Portals - Group 3 (Careers & Internships)
------------------------------------------------
This Django project implements the functionality for Group 3: Careers & Internships.
Features:
  - CareerOpportunity model (company, role, deadline, link, description)
  - Save/Unsave (bookmarks) for logged-in students
  - Apply to opportunities (stores Application and notifies student)
  - In-app Notifications stored and displayed (unread at top; viewing marks read)
  - Sorting / filtering and a simple recommendation system based on StudentProfile.skills or enrolled_subjects
  - Admin interface for managing data

Quick start (run locally):
  1. Create a virtualenv and install requirements: pip install -r requirements.txt
  2. Run migrations: python manage.py migrate
  3. Populate sample data: python manage.py populate_sample
  4. Start server: python manage.py runserver
  5. Login at /admin/ with the sample user student1 / password123 (created by populate_sample)

Files included: manage.py, student_portal/*, careers/*, templates/*, static (optional)
