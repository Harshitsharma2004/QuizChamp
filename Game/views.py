from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from random import sample
from .forms import RegisterForm, EditProfileForm, ChangePasswordForm
from .models import CustomUser, Category, Question
from .models import QuizResult  # ✅ Importing QuizResult
from django.db.models import Max, Sum  # ✅ Aggregation functions
import csv
import random
import requests
from django.core.files.storage import default_storage

User = get_user_model()

def home(request):
    return render(request,'game/home.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            user.generate_otp()
            user.save(update_fields=["otp"])
            mail_subject = "Your QuizChamp OTP Verification Code"
            message = f"Hello {user.username},\n\nYour OTP for QuizChamp account verification is: {user.otp}\n\nThis OTP is valid for 5 minutes."
            send_mail(mail_subject, message, "noreply@example.com", [user.email])
            messages.success(request, "An OTP has been sent to your email. Please enter it below to verify your account.")
            return redirect("verify_email", user_id=user.id)
    else:
        form = RegisterForm()
    return render(request, "game/register.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been verified. You can now log in.")
        return redirect('login')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('home')

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            if user.email_verified and user.is_active:
                login(request, user)
                messages.success(request, "Login successful! Welcome to QuizChamp! 🏆")
                return redirect("home")
            else:
                messages.error(request, "Your email is not verified. Please enter the OTP sent to your email.")
                return redirect("verify_email", user_id=user.id)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "game/login.html")

def verify_email(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect("register")
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if user.is_otp_valid(entered_otp):
            user.email_verified = True
            user.is_active = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            messages.success(request, "Email verified successfully! You can now log in.")
            return redirect("login")
        else:
            messages.error(request, "Invalid or expired OTP. Please try again.")
    return render(request, "game/verify_email.html", {"user_id": user.id})

@login_required
def profile(request):
    return render(request, "game/profile.html", {"user": request.user})

@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = EditProfileForm(instance=user)
    return render(request, "game/edit_profile.html", {"form": form})

@login_required
def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Your password was updated successfully.")
            return redirect("profile")
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, "game/change_password.html", {"form": form})

@login_required
def delete_account(request):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")
    return render(request, "game/delete_account.html")

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")

@login_required
def dashboard(request):
    user = request.user

    games_played = QuizResult.objects.filter(user=user).count()

    # Category-wise scores for current user
    category_qs = (
        QuizResult.objects.filter(user=user)
        .values('category__name')
        .annotate(score=Sum('score'))
    )
    category_labels = [entry['category__name'] for entry in category_qs]
    category_scores = [entry['score'] for entry in category_qs]

    return render(request, 'game/dashboard.html', {
        'category_labels': category_labels,
        'category_scores': category_scores,
        'games_played': games_played,
    })
otp_storage = {}

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        users = CustomUser.objects.filter(email=email)
        if users.exists():
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['email'] = email
            messages.success(request, 'OTP sent to your email!')
            return redirect('verify_otp')
        else:
            messages.error(request, 'No account found with this email!')
    return render(request, 'reset/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        email = request.session.get('email')
        entered_otp = request.POST['otp']
        if email in otp_storage and str(otp_storage[email]) == entered_otp:
            del otp_storage[email]
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP!')
    return render(request, 'reset/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        email = request.session.get('email')
        new_password = request.POST['password']
        users = CustomUser.objects.filter(email=email)
        if users.exists():
            for user in users:
                user.set_password(new_password)
                user.save()
            messages.success(request, 'Password reset successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Error resetting password.')
    return render(request, 'reset/reset_password.html')

@login_required
def select_category(request):
    categories = Category.objects.all()
    return render(request, 'quiz/select_category.html', {'categories': categories})

@login_required
def start_quiz(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        all_questions = list(Question.objects.filter(category_id=category_id))
        
        if len(all_questions) <= 30:
            questions = all_questions
        else:
            questions = sample(all_questions, 30)
        
        request.session['quiz_questions'] = [q.id for q in questions]
        request.session['quiz_score'] = 0
        request.session['quiz_index'] = 0
        return redirect('quiz_question')
    return redirect('select_category')

@login_required
def quiz_question(request):
    question_ids = request.session.get('quiz_questions', [])
    index = request.session.get('quiz_index', 0)
    
    # Check if all questions are answered
    if index >= len(question_ids):
        return redirect('quiz_result')
    
    question = Question.objects.get(id=question_ids[index])
    
    # Prepare the list of options to pass to the template
    options = [question.option1, question.option2, question.option3, question.option4]
    
    # Pop last correct answer and result from session
    last_correct = request.session.pop('last_correct_answer', None)
    last_result = request.session.pop('last_answer_correct', None)

    return render(request, 'quiz/quiz_question.html', {
        'question': question,
        'options': options,
        'index': index + 1,
        'total': len(question_ids),
        'last_correct': last_correct,
        'last_result': last_result,
    })

@login_required
def submit_answer(request):
    if request.method == 'POST':
        selected = request.POST.get('selected_answer')
        question_id = request.POST.get('question_id')
        question = Question.objects.get(id=question_id)
        is_correct = selected == question.correct_answer

        if is_correct:
            request.session['quiz_score'] += 1

        request.session['quiz_index'] += 1
        request.session['last_answer_correct'] = is_correct
        request.session['last_correct_answer'] = question.correct_answer
        return redirect('quiz_question')
    return redirect('select_category')

@login_required
def quiz_result(request):
    score = request.session.get('quiz_score', 0)
    question_ids = request.session.get('quiz_questions', [])
    total = len(question_ids)

    if question_ids:
        first_question = Question.objects.get(id=question_ids[0])
        QuizResult.objects.create(
            user=request.user,
            category=first_question.category,  # Pass the actual Category object
            score=score
        )

    # Clear session
    request.session.pop('quiz_score', None)
    request.session.pop('quiz_index', None)
    request.session.pop('quiz_questions', None)

    response = render(request, 'quiz/result.html', {'score': score, 'total': total})
    response.set_cookie('clear_timer', 'true', max_age=3)
    return response
#facts 
def general_facts(request):
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    facts = []

    # Fetch 5 random facts
    for _ in range(10):
        response = requests.get(url)
        if response.status_code == 200:
            fact = response.json().get("text")
            if fact:
                facts.append(fact)

    return render(request, "game/general_facts.html", {"facts": facts})


@staff_member_required
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV format.')
            return redirect('upload_csv')

        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(file_data)

        for row in reader:
            Question.objects.create(
                question=row['question'],
                option1=row['option1'],
                option2=row['option2'],
                option3=row['option3'],
                option4=row['option4'],
                correct_answer=row['correct_answer'],
                category=Category.objects.get_or_create(name=row['category'])[0]
            )

        messages.success(request, 'CSV uploaded and questions saved successfully!')
        return redirect('upload_csv')

    return render(request, 'admin/upload_csv.html')