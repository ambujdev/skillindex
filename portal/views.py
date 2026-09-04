from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from .models import (
    UserProfile, AcademicRecord, Skill, StudentSkill,
    Project, Certificate, Achievement, InternshipJob, Application
)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', 'STUDENT')
        institution_or_company = request.POST.get('institution_or_company', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'auth/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.institution_or_company = institution_or_company
        profile.save()

        if role == 'STUDENT':
            AcademicRecord.objects.get_or_create(profile=profile)

        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('dashboard')

    return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

@login_required
def dashboard_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.role == 'STUDENT':
        return student_dashboard_view(request, profile)
    elif profile.role == 'INDUSTRY':
        return industry_dashboard_view(request, profile)
    else:
        return academia_dashboard_view(request, profile)

def student_dashboard_view(request, profile):
    academic, _ = AcademicRecord.objects.get_or_create(profile=profile)
    student_skills = StudentSkill.objects.filter(profile=profile).select_related('skill').order_by('-proficiency_percentage')
    top_skills = student_skills[:5]
    all_skills = Skill.objects.all()
    projects = Project.objects.filter(profile=profile)
    certificates = Certificate.objects.filter(profile=profile)
    achievements = Achievement.objects.filter(profile=profile)
    applications = Application.objects.filter(student=profile).select_related('job')
    
    # Recent activity calculation
    recent_activity = []
    for app in applications[:3]:
        recent_activity.append({
            'icon': 'briefcase',
            'title': f"Application {app.get_status_display()} at {app.job.company_name}",
            'subtitle': f"{app.job.title} • {app.applied_at.strftime('%b %d, %Y')}",
            'color': 'primary' if app.status == 'ACCEPTED' else 'info'
        })
    for proj in projects[:2]:
        recent_activity.append({
            'icon': 'code',
            'title': f"Completed Project: {proj.title}",
            'subtitle': proj.tech_stack,
            'color': 'success'
        })
    for cert in certificates[:2]:
        recent_activity.append({
            'icon': 'award',
            'title': f"Earned Certificate in {cert.title}",
            'subtitle': f"{cert.issuer} • {cert.issue_date.strftime('%b %Y')}",
            'color': 'warning'
        })

    # Featured Internship for card view (matching Google software engineering intern card in prompt)
    accepted_internship = applications.filter(job__opportunity_type='INTERNSHIP').first()

    context = {
        'profile': profile,
        'academic': academic,
        'student_skills': student_skills,
        'top_skills': top_skills,
        'all_skills': all_skills,
        'projects': projects,
        'certificates': certificates,
        'achievements': achievements,
        'applications': applications,
        'recent_activity': recent_activity,
        'accepted_internship': accepted_internship,
    }
    return render(request, 'student/dashboard.html', context)

def industry_dashboard_view(request, profile):
    posted_jobs = InternshipJob.objects.filter(posted_by=profile).annotate(applicant_count=Count('job_applications'))
    total_applicants = Application.objects.filter(job__posted_by=profile).count()
    shortlisted = Application.objects.filter(job__posted_by=profile, status='ACCEPTED').count()
    under_review = Application.objects.filter(job__posted_by=profile, status='UNDER_REVIEW').count()
    
    # Search candidates by skill or name
    query = request.GET.get('q', '')
    candidates = UserProfile.objects.filter(role='STUDENT').select_related('academic_record')
    if query:
        candidates = candidates.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(student_skills__skill__name__icontains=query) |
            Q(institution_or_company__icontains=query)
        ).distinct()

    context = {
        'profile': profile,
        'posted_jobs': posted_jobs,
        'total_applicants': total_applicants,
        'shortlisted': shortlisted,
        'under_review': under_review,
        'candidates': candidates[:10],
        'query': query,
    }
    return render(request, 'industry/dashboard.html', context)

def academia_dashboard_view(request, profile):
    total_students = UserProfile.objects.filter(role='STUDENT').count()
    total_industry_partners = UserProfile.objects.filter(role='INDUSTRY').count()
    total_jobs = InternshipJob.objects.count()
    placed_students = Application.objects.filter(status='ACCEPTED').values('student').distinct().count()
    
    placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 84.5
    avg_cgpa = AcademicRecord.objects.aggregate(avg=Avg('cgpa'))['avg'] or 8.2

    # Top skills distribution
    top_demanded_skills = Skill.objects.annotate(job_count=Count('job_requirements')).order_by('-job_count')[:6]
    student_skill_stats = Skill.objects.annotate(student_count=Count('studentskill')).order_by('-student_count')[:6]

    context = {
        'profile': profile,
        'total_students': total_students,
        'total_industry_partners': total_industry_partners,
        'total_jobs': total_jobs,
        'placed_students': placed_students,
        'placement_rate': placement_rate,
        'avg_cgpa': round(avg_cgpa, 2),
        'top_demanded_skills': top_demanded_skills,
        'student_skill_stats': student_skill_stats,
    }
    return render(request, 'academia/dashboard.html', context)

@login_required
def skills_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        new_skill_name = request.POST.get('new_skill_name')
        proficiency = int(request.POST.get('proficiency', 80))
        level = request.POST.get('level', 'ADVANCED')

        if new_skill_name:
            skill, _ = Skill.objects.get_or_create(name=new_skill_name.strip(), defaults={'category': 'TECHNICAL'})
        elif skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
        else:
            messages.error(request, "Please select or enter a skill name.")
            return redirect('skills')

        student_skill, created = StudentSkill.objects.get_or_create(
            profile=profile,
            skill=skill,
            defaults={'proficiency_percentage': proficiency, 'level': level}
        )
        if not created:
            student_skill.proficiency_percentage = proficiency
            student_skill.level = level
            student_skill.save()

        messages.success(request, f"Skill '{skill.name}' updated successfully!")
        return redirect('skills')

    student_skills = StudentSkill.objects.filter(profile=profile).select_related('skill')
    all_skills = Skill.objects.all()

    # Skill Gap Mapping logic: skills requested by open industry jobs vs student skills
    job_required_skills = Skill.objects.filter(job_requirements__is_active=True).annotate(demand=Count('job_requirements')).order_by('-demand')
    my_skill_ids = set(student_skills.values_list('skill_id', flat=True))
    
    skill_gaps = []
    for sk in job_required_skills:
        skill_gaps.append({
            'skill': sk,
            'demand_count': sk.demand,
            'is_possessed': sk.id in my_skill_ids,
        })

    context = {
        'profile': profile,
        'student_skills': student_skills,
        'all_skills': all_skills,
        'skill_gaps': skill_gaps,
    }
    return render(request, 'student/skills.html', context)

@login_required
def profile_view(request):
    profile = request.user.profile
    academic, _ = AcademicRecord.objects.get_or_create(profile=profile)
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        profile.bio = request.POST.get('bio', profile.bio)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.institution_or_company = request.POST.get('institution_or_company', profile.institution_or_company)
        profile.department = request.POST.get('department', profile.department)
        profile.branch_and_year = request.POST.get('branch_and_year', profile.branch_and_year)
        profile.location = request.POST.get('location', profile.location)
        profile.linkedin_url = request.POST.get('linkedin_url', profile.linkedin_url)
        profile.github_url = request.POST.get('github_url', profile.github_url)
        if request.POST.get('avatar_url'):
            profile.avatar_url = request.POST.get('avatar_url')
        profile.save()

        if profile.role == 'STUDENT':
            academic.degree = request.POST.get('degree', academic.degree)
            try:
                academic.cgpa = float(request.POST.get('cgpa', academic.cgpa))
                academic.passing_year = int(request.POST.get('passing_year', academic.passing_year))
            except ValueError:
                pass
            academic.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    context = {
        'profile': profile,
        'academic': academic,
    }
    return render(request, 'student/profile.html', context)

@login_required
def resume_view(request):
    profile = request.user.profile
    academic, _ = AcademicRecord.objects.get_or_create(profile=profile)
    student_skills = StudentSkill.objects.filter(profile=profile).select_related('skill')
    projects = Project.objects.filter(profile=profile)
    certificates = Certificate.objects.filter(profile=profile)
    achievements = Achievement.objects.filter(profile=profile)

    context = {
        'profile': profile,
        'academic': academic,
        'student_skills': student_skills,
        'projects': projects,
        'certificates': certificates,
        'achievements': achievements,
    }
    return render(request, 'student/resume.html', context)

@login_required
def job_list_view(request):
    query = request.GET.get('q', '')
    opportunity_type = request.GET.get('type', '')
    
    jobs = InternshipJob.objects.filter(is_active=True).prefetch_related('required_skills')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(required_skills__name__icontains=query) |
            Q(location__icontains=query)
        ).distinct()
    
    if opportunity_type:
        jobs = jobs.filter(opportunity_type=opportunity_type)

    user_applications = set()
    if request.user.profile.role == 'STUDENT':
        user_applications = set(Application.objects.filter(student=request.user.profile).values_list('job_id', flat=True))

    context = {
        'jobs': jobs,
        'query': query,
        'opportunity_type': opportunity_type,
        'user_applications': user_applications,
    }
    return render(request, 'jobs/list.html', context)

@login_required
def job_detail_view(request, job_id):
    job = get_object_or_404(InternshipJob, id=job_id)
    profile = request.user.profile
    
    has_applied = False
    application = None
    if profile.role == 'STUDENT':
        application = Application.objects.filter(student=profile, job=job).first()
        has_applied = application is not None

    if request.method == 'POST' and profile.role == 'STUDENT':
        if not has_applied:
            cover_note = request.POST.get('cover_note', '')
            Application.objects.create(
                student=profile,
                job=job,
                cover_note=cover_note,
                status='APPLIED'
            )
            messages.success(request, f"Successfully applied for {job.title} at {job.company_name}!")
            return redirect('job_detail', job_id=job.id)

    context = {
        'job': job,
        'has_applied': has_applied,
        'application': application,
    }
    return render(request, 'jobs/detail.html', context)

@login_required
def job_create_view(request):
    profile = request.user.profile
    if profile.role != 'INDUSTRY' and not request.user.is_staff:
        messages.error(request, "Only Industry partners can post opportunities.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        company_name = request.POST.get('company_name', profile.institution_or_company or 'Tech Corp')
        opportunity_type = request.POST.get('opportunity_type', 'INTERNSHIP')
        location = request.POST.get('location', 'Hybrid')
        stipend_or_salary = request.POST.get('stipend_or_salary', '₹50,000 / month')
        description = request.POST.get('description', '')
        min_cgpa = float(request.POST.get('min_cgpa', 7.0))
        deadline = request.POST.get('deadline')
        skill_ids = request.POST.getlist('skills')

        job = InternshipJob.objects.create(
            posted_by=profile,
            title=title,
            company_name=company_name,
            opportunity_type=opportunity_type,
            location=location,
            stipend_or_salary=stipend_or_salary,
            description=description,
            min_cgpa=min_cgpa,
            deadline=deadline if deadline else date.today() + timedelta(days=30),
        )
        if skill_ids:
            job.required_skills.set(skill_ids)

        messages.success(request, f"Opportunity '{title}' posted successfully!")
        return redirect('industry_dashboard')

    all_skills = Skill.objects.all()
    return render(request, 'industry/job_create.html', {'all_skills': all_skills})

@login_required
def applicants_view(request, job_id=None):
    profile = request.user.profile
    if profile.role != 'INDUSTRY' and profile.role != 'ACADEMIA':
        messages.error(request, "Access restricted.")
        return redirect('dashboard')

    if job_id:
        job = get_object_or_404(InternshipJob, id=job_id)
        applications = Application.objects.filter(job=job).select_related('student__user', 'student__academic_record')
    else:
        job = None
        applications = Application.objects.filter(job__posted_by=profile).select_related('job', 'student__user', 'student__academic_record')

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        recruiter_notes = request.POST.get('recruiter_notes', '')

        app = get_object_or_404(Application, id=app_id)
        app.status = new_status
        if recruiter_notes:
            app.recruiter_notes = recruiter_notes
        app.save()

        messages.success(request, f"Application status updated to {app.get_status_display()}.")
        return redirect('applicants_by_job', job_id=app.job.id) if job else redirect('applicants')

    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'industry/applicants.html', context)

@login_required
def applications_view(request):
    profile = request.user.profile
    applications = Application.objects.filter(student=profile).select_related('job')
    return render(request, 'student/applications.html', {'applications': applications})
