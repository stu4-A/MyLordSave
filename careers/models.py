# careers/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# -------------------------------
# User Profile for Role-Based Access
# -------------------------------
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# -------------------------------
# Student Profile
# -------------------------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    skills = models.TextField(blank=True, help_text='Comma-separated skills like Python,SQL')
    enrolled_subjects = models.TextField(blank=True, help_text='Comma-separated subject names')

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# -------------------------------
# Career Opportunity
# -------------------------------
class CareerOpportunity(models.Model):
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=300)
    deadline = models.DateField()
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_opportunities')

    def __str__(self):
        return f"{self.company} - {self.role}"


# -------------------------------
# Saved Opportunity (Student)
# -------------------------------
class SavedOpportunity(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='saved_opportunities')
    opportunity = models.ForeignKey(CareerOpportunity, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'opportunity')

    def __str__(self):
        return f"{self.student} saved {self.opportunity}"


# -------------------------------
# Application (Student)
# -------------------------------
class Application(models.Model):
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE)
    opportunity = models.ForeignKey('CareerOpportunity', on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} applied for {self.opportunity.role}"

# -------------------------------
# Notification (Student)
# -------------------------------
class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.student}: {self.message[:40]}"


# -------------------------------
# Signals: create UserProfile automatically if missing
# -------------------------------
@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    # Always ensure a UserProfile exists for every User (default role=student).
    if created:
        UserProfile.objects.create(user=instance, role='student')
    else:
        # if user exists but profile missing (legacy), create with default
        if not hasattr(instance, 'userprofile'):
            UserProfile.objects.create(user=instance, role='student')
