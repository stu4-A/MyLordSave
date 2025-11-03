# careers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import CareerOpportunity, StudentProfile, SavedOpportunity, Application, Notification, UserProfile
from .forms import ApplicationForm, ProfileForm, RegistrationForm, OpportunityForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.views.decorators.http import require_POST
from .decorators import student_required, lecturer_required
from django.urls import reverse

# Custom Login View (redirect by role)
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        profile = getattr(self.request.user, 'userprofile', None) or UserProfile.objects.filter(user=self.request.user).first()
        if profile and profile.role == 'lecturer':
            return reverse('manage_opportunities')  # ✅ corrected
        return reverse('opportunity_list')

# Home
def home_page(request):
    return render(request, 'careers/home.html')

# Helper: return StudentProfile for logged-in student (or None)
def get_student_profile_for_request(request):
    if not request.user.is_authenticated:
        return None
    profile = getattr(request.user, 'userprofile', None) or UserProfile.objects.filter(user=request.user).first()
    if not profile or profile.role != 'student':
        return None
    sp, _ = StudentProfile.objects.get_or_create(user=request.user)
    return sp

# Opportunity list (student)
@login_required
@student_required
def opportunity_list(request):
    qs = CareerOpportunity.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(company__icontains=q) | Q(role__icontains=q) | Q(description__icontains=q)
        )
    filt = request.GET.get('filter', '')
    if filt == 'deadline':
        qs = qs.order_by('deadline')
    elif filt == 'newest':
        qs = qs.order_by('-created_at')
    else:
        qs = qs.order_by('deadline')
    opportunities = qs[:200]

    # recommendations from student profile
    recommendations = []
    sp = get_student_profile_for_request(request)
    if sp:
        subjects_str = sp.enrolled_subjects or ''
        skills_str = sp.skills or ''
        keywords = {k.strip().lower() for k in (subjects_str + ',' + skills_str).split(',') if k.strip()}
        for opp in opportunities:
            roletext = f"{opp.role or ''} {opp.description or ''}".lower()
            if any(k in roletext for k in keywords):
                recommendations.append(opp)
        recommendations = list(dict.fromkeys(recommendations))[:5]

    context = {'opportunities': opportunities, 'q': q, 'filter': filt, 'recommendations': recommendations}
    return render(request, 'careers/opportunity_list.html', context)

# Opportunity detail (student)
@login_required
@student_required
def opportunity_detail(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)
    saved = SavedOpportunity.objects.filter(student=sp, opportunity=opp).exists() if sp else False
    applied = Application.objects.filter(student=sp, opportunity=opp).exists() if sp else False
    form = ApplicationForm()
    return render(request, 'careers/opportunity_detail.html', {'opp': opp, 'saved': saved, 'applied': applied, 'form': form})

# Save/unsave (student)
@login_required
@student_required
@require_POST
def save_toggle(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)
    if not sp:
        messages.error(request, 'Student profile not found.')
        return redirect('opportunity_list')
    so = SavedOpportunity.objects.filter(student=sp, opportunity=opp)
    if so.exists():
        so.delete()
        messages.success(request, 'Opportunity removed from saved list.')
    else:
        SavedOpportunity.objects.create(student=sp, opportunity=opp)
        Notification.objects.create(student=sp, message=f'You saved opportunity: {opp.company} - {opp.role}', date=timezone.now())
        messages.success(request, 'Opportunity saved.')
    return redirect('opportunity_detail', pk=pk)

# Apply (student)
@login_required
@student_required
@require_POST
def apply_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk)
    sp = get_student_profile_for_request(request)

    if not sp:
        messages.error(request, 'Student profile not found.')
        return redirect('opportunity_list')

    # Prevent duplicate applications
    if Application.objects.filter(student=sp, opportunity=opp).exists():
        messages.warning(request, 'You already applied for this opportunity.')
        return redirect('opportunity_detail', pk=pk)

    form = ApplicationForm(request.POST)
    if form.is_valid():
        app = form.save(commit=False)
        app.student = sp
        app.opportunity = opp
        app.save()

        # Send a notification
        Notification.objects.create(
            student=sp,
            message=f'Application submitted for {opp.role} at {opp.company}',
            date=timezone.now()
        )

        messages.success(request, 'Your application has been successfully submitted!')
    else:
        messages.error(request, 'There was an issue with your application.')

    return redirect('opportunity_detail', pk=pk)

# Notifications (student)
@login_required
@student_required
def notifications_view(request):
    sp = get_student_profile_for_request(request)

    if not sp:
        # If no student profile found, show empty list
        return render(request, 'careers/notifications.html', {'notifications': []})

    # Get all notifications for this student (ordered)
    notifications_qs = Notification.objects.filter(student=sp).order_by('-date')

    # Mark all as read first (no slicing here)
    notifications_qs.update(read=True)

    # Then slice for display
    notifications = notifications_qs[:20]

    return render(request, 'careers/notifications.html', {'notifications': notifications})


# Register
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role', 'student')
            # ensure a UserProfile exists with correct role
            UserProfile.objects.get_or_create(user=user, defaults={'role': role})
            if role == 'student':
                StudentProfile.objects.get_or_create(user=user)
            login(request, user)
            # ✅ Use named URL for lecturer
            if role == 'lecturer':
                return redirect('manage_opportunities')
            return redirect('opportunity_list')
    else:
        form = RegistrationForm()
    return render(request, 'careers/register.html', {'form': form})

# Edit Profile (student)
@login_required
@student_required
def edit_profile(request):
    sp = get_student_profile_for_request(request)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=sp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('opportunity_list')
    else:
        form = ProfileForm(instance=sp)
    return render(request, 'careers/edit_profile.html', {'form': form})

# Profile redirect
def profile_redirect(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'userprofile', None) or UserProfile.objects.filter(user=request.user).first()
        if profile and profile.role == 'lecturer':
            return redirect('manage_opportunities')  # ✅ corrected
        return redirect('opportunity_list')
    return redirect('login')

# Lecturer views
@login_required
@lecturer_required
def create_opportunity(request):
    if request.method == 'POST':
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opp = form.save(commit=False)
            opp.posted_by = request.user
            opp.save()
            messages.success(request, 'Opportunity posted successfully!')
            return redirect('manage_opportunities')
    else:
        form = OpportunityForm()
    return render(request, 'careers/create_opportunity.html', {'form': form})

@login_required
@lecturer_required
def manage_opportunities(request):
    opportunities = CareerOpportunity.objects.filter(posted_by=request.user)
    return render(request, 'careers/manage_opportunities.html', {'opportunities': opportunities})

@login_required
@lecturer_required
def edit_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = OpportunityForm(request.POST, instance=opp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Opportunity updated successfully!')
            return redirect('manage_opportunities')
    else:
        form = OpportunityForm(instance=opp)
    return render(request, 'careers/create_opportunity.html', {'form': form, 'edit': True})

@login_required
@lecturer_required
def delete_opportunity(request, pk):
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        opp.delete()
        messages.success(request, 'Opportunity deleted successfully!')
        return redirect('manage_opportunities')
    return render(request, 'careers/delete_confirmation.html', {'opp': opp})

@login_required
@lecturer_required
def view_applications(request, pk):
    """Lecturer can see all applications for one of their posted opportunities."""
    opp = get_object_or_404(CareerOpportunity, pk=pk, posted_by=request.user)
    applications = Application.objects.filter(opportunity=opp).select_related('student', 'student__user')
    return render(request, 'careers/view_applications.html', {'opp': opp, 'applications': applications})
