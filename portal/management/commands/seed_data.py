from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import (
    UserProfile, AcademicRecord, Skill, StudentSkill,
    Project, Certificate, Achievement, InternshipJob, Application
)
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seeds initial realistic data for Skill Index portal'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding Skill Index data...")

        # 1. Create Core Skills
        skills_data = [
            ('Python', 'TECHNICAL'),
            ('C++', 'TECHNICAL'),
            ('Web Development', 'TECHNICAL'),
            ('SQL', 'TECHNICAL'),
            ('JavaScript', 'TECHNICAL'),
            ('Machine Learning', 'TECHNICAL'),
            ('Data Structures', 'TECHNICAL'),
            ('Django', 'TECHNICAL'),
            ('PostgreSQL', 'TECHNICAL'),
            ('Cloud Computing', 'TECHNICAL'),
            ('Problem Solving', 'SOFT'),
            ('Team Leadership', 'SOFT'),
            ('Agile Methodology', 'DOMAIN'),
        ]

        skill_objs = {}
        for name, category in skills_data:
            s, _ = Skill.objects.get_or_create(name=name, defaults={'category': category})
            skill_objs[name] = s

        # 2. Create Student User (Ananya Sharma - matching prompt image)
        student_user, _ = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'ananya.sharma@dtu.ac.in',
                'first_name': 'Ananya',
                'last_name': 'Sharma',
                'is_staff': False,
            }
        )
        student_user.set_password('password123')
        student_user.save()

        student_profile, _ = UserProfile.objects.get_or_create(
            user=student_user,
            defaults={
                'role': 'STUDENT',
                'phone': '+91 98765 43210',
                'bio': 'Motivated Computer Science student with strong problem-solving skills and passion for building real-world solutions.',
                'institution_or_company': 'Delhi Technological University',
                'department': 'Computer Science & Engineering',
                'designation': 'B.Tech 4th Year',
                'location': 'Delhi, India',
                'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=250&q=80',
            }
        )
        student_profile.role = 'STUDENT'
        student_profile.save()

        AcademicRecord.objects.get_or_create(
            profile=student_profile,
            defaults={
                'degree': 'B.Tech Computer Science',
                'cgpa': 8.76,
                'max_cgpa': 10.00,
                'passing_year': 2026,
                'completed_internships_count': 2,
                'earned_achievements_count': 8,
            }
        )

        # Attach Student Skills with realistic proficiencies
        student_skills_def = [
            ('Python', 90, 'EXPERT'),
            ('C++', 80, 'ADVANCED'),
            ('Web Development', 75, 'ADVANCED'),
            ('SQL', 70, 'INTERMEDIATE'),
            ('JavaScript', 70, 'INTERMEDIATE'),
            ('Machine Learning', 65, 'INTERMEDIATE'),
            ('Data Structures', 85, 'EXPERT'),
        ]
        for sname, pct, lvl in student_skills_def:
            if sname in skill_objs:
                StudentSkill.objects.get_or_create(
                    profile=student_profile,
                    skill=skill_objs[sname],
                    defaults={
                        'proficiency_percentage': pct,
                        'level': lvl,
                        'verified_by_academia': True
                    }
                )

        # Student Projects
        Project.objects.get_or_create(
            profile=student_profile,
            title='Smart Attendance System',
            defaults={
                'description': 'AI-driven face recognition attendance tracking system using Python, OpenCV and Django with real-time analytics.',
                'tech_stack': 'Python, Django, OpenCV, PostgreSQL',
                'project_url': 'https://github.com/ananya/smart-attendance'
            }
        )
        Project.objects.get_or_create(
            profile=student_profile,
            title='Skill Mapping & Placement Analytics',
            defaults={
                'description': 'Interactive portal mapping academic curriculum to industry skill demands.',
                'tech_stack': 'JavaScript, HTML/CSS, Python, Django',
                'project_url': 'https://github.com/ananya/skill-index'
            }
        )

        # Student Certificates & Achievements
        Certificate.objects.get_or_create(
            profile=student_profile,
            title='Advanced Python Programming & Data Science',
            defaults={
                'issuer': 'HackerRank & IBM',
                'issue_date': date(2025, 6, 15),
                'credential_url': 'https://example.com/cert/python-ds'
            }
        )

        Achievement.objects.get_or_create(
            profile=student_profile,
            title='1st Place - DTU Hackathon 2025',
            defaults={'description': 'Awarded best innovation for AI-powered student mentorship platform.'}
        )

        # 3. Create Industry Recruiter User
        industry_user, _ = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter@google.com',
                'first_name': 'Rohan',
                'last_name': 'Verma',
            }
        )
        industry_user.set_password('password123')
        industry_user.save()

        industry_profile, _ = UserProfile.objects.get_or_create(
            user=industry_user,
            defaults={
                'role': 'INDUSTRY',
                'phone': '+91 91234 56789',
                'bio': 'University Relations & Technical Talent Lead at Google India.',
                'institution_or_company': 'Google India',
                'department': 'Global Talent Acquisition',
                'designation': 'Senior Engineering Recruiter',
                'location': 'Bengaluru / Gurgaon, India',
                'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=250&q=80',
            }
        )

        # 4. Create Academia Admin User
        academia_user, _ = User.objects.get_or_create(
            username='admin1',
            defaults={
                'email': 'placement@dtu.ac.in',
                'first_name': 'Dr. Priya',
                'last_name': 'Sharma',
                'is_staff': True,
            }
        )
        academia_user.set_password('password123')
        academia_user.save()

        UserProfile.objects.get_or_create(
            user=academia_user,
            defaults={
                'role': 'ACADEMIA',
                'phone': '+91 99887 76655',
                'bio': 'Head of Training & Placement Cell, DTU. Dedicated to aligning student skills with industry 4.0 standards.',
                'institution_or_company': 'Delhi Technological University',
                'department': 'Training & Placement Directorate',
                'designation': 'Director of Training & Placement',
                'location': 'Delhi, India',
                'avatar_url': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=250&q=80',
            }
        )

        # 5. Create Industry Job / Internship Postings
        job1, _ = InternshipJob.objects.get_or_create(
            title='Software Engineering Intern',
            company_name='Google India',
            defaults={
                'posted_by': industry_profile,
                'company_logo': 'https://cdn-icons-png.flaticon.com/512/2991/2991148.png',
                'opportunity_type': 'INTERNSHIP',
                'location': 'Bengaluru / Gurgaon (Hybrid)',
                'stipend_or_salary': '₹85,000 / month',
                'description': 'Work on real-time scalable backend systems, collaborate with international engineering teams, and optimize core search/cloud services.',
                'min_cgpa': 8.00,
                'deadline': date.today() + timedelta(days=30),
                'is_active': True,
            }
        )
        job1.required_skills.set([skill_objs['Python'], skill_objs['C++'], skill_objs['Data Structures']])

        job2, _ = InternshipJob.objects.get_or_create(
            title='Full Stack Web Developer',
            company_name='Reliance Retail Tech',
            defaults={
                'posted_by': industry_profile,
                'company_logo': 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
                'opportunity_type': 'FULL_TIME',
                'location': 'Mumbai, India',
                'stipend_or_salary': '14.5 - 18.0 LPA',
                'description': 'Build high-throughput e-commerce microservices, integrate frontend dashboard user experiences, and maintain high performance web applications.',
                'min_cgpa': 7.50,
                'deadline': date.today() + timedelta(days=45),
                'is_active': True,
            }
        )
        job2.required_skills.set([skill_objs['Web Development'], skill_objs['JavaScript'], skill_objs['Django'], skill_objs['SQL']])

        job3, _ = InternshipJob.objects.get_or_create(
            title='AI & Machine Learning Research Intern',
            company_name='Microsoft Research India',
            defaults={
                'posted_by': industry_profile,
                'company_logo': 'https://cdn-icons-png.flaticon.com/512/732/732221.png',
                'opportunity_type': 'INTERNSHIP',
                'location': 'Bengaluru, India',
                'stipend_or_salary': '₹95,000 / month',
                'description': 'Conduct exploratory research in Large Language Model fine-tuning, computer vision, and responsible AI system architectures.',
                'min_cgpa': 8.50,
                'deadline': date.today() + timedelta(days=20),
                'is_active': True,
            }
        )
        job3.required_skills.set([skill_objs['Python'], skill_objs['Machine Learning'], skill_objs['Problem Solving']])

        # 6. Applications
        Application.objects.get_or_create(
            student=student_profile,
            job=job1,
            defaults={
                'status': 'ACCEPTED',
                'cover_note': 'Worked on real-time projects and improved system performance by 15%.',
                'recruiter_notes': 'Selected for outstanding performance in technical interview round.'
            }
        )

        Application.objects.get_or_create(
            student=student_profile,
            job=job2,
            defaults={
                'status': 'UNDER_REVIEW',
                'cover_note': 'Eager to apply Django and full-stack web development expertise to scale enterprise applications.',
                'recruiter_notes': 'Shortlisted based on strong CGPA and project portfolio.'
            }
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded Skill Index demo data!"))
