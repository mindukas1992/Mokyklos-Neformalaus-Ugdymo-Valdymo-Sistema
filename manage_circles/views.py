import csv
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import User
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .forms import ParentForm, ChildForm, EnrollmentForm, ContactForm
from .models import Parent, Child, Club, Enrollment


def home(request):
    activities = Club.objects.all()
    return render(request, 'home.html', {'activities': activities})


@login_required
def edit_parent(request, pk):
    parent = get_object_or_404(Parent, pk=pk)
    if request.method == 'POST':
        form = ParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = ParentForm(instance=parent)
    return render(request, 'edit_parent.html', {'form': form})


@login_required
def edit_child(request, pk):
    child = get_object_or_404(Child, pk=pk)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = ChildForm(instance=child)
    return render(request, 'edit_child.html', {'form': form, 'child': child})


@require_POST
def delete_child(request, child_id):
    child = Child.objects.get(id=child_id)
    return render(request, 'delete_child.html', {'child': child})


def confirm_delete_child(request, child_id):
    child = Child.objects.get(id=child_id)
    child.delete()
    return redirect('my_profile')


@login_required
def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            new_child = form.save(commit=False)
            new_child.parent = request.user.parent
            new_child.save()
            return redirect('my_profile')
    else:
        form = ChildForm()
    return render(request, 'add_child.html', {'form': form})


@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if not User.objects.filter(username=username).exists() and not User.objects.filter(email=email).exists():
                User.objects.create_user(username=username, email=email, password=password)
                messages.info(request, f'Vartotojas {username} užregistruotas!')
                return redirect('login')
            else:
                if User.objects.filter(username=username).exists():
                    messages.error(request, f'Vartotojo vardas {username} užimtas!')
                else:
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
    return render(request, 'register.html')


@login_required
def my_profile(request):
    parent, created = Parent.objects.get_or_create(user=request.user)
    children = parent.children.all()
    enrolled_clubs = []
    for child in children:
        enrollments = child.enrollments.select_related('session__club').all()
        for enrollment in enrollments:
            club_name = enrollment.session.club.name
            child_name = f"{child.first_name} {child.last_name}"
            registration_date = enrollment.registration_date
            session = f"{enrollment.session.day_of_week} {enrollment.session.start_time}-{enrollment.session.end_time} ({enrollment.session.group})"
            enrolled_clubs.append({'club_name': club_name, 'child_name': child_name, 'registration_date': registration_date, 'session': session, 'enrollment_id': enrollment.id})
    return render(request, 'my_profile.html', {'parent': parent, 'children': children, 'enrolled_clubs': enrolled_clubs})


def artistic_activities(request):
    clubs = Club.objects.filter(activity_type='artistic')
    selected_club_id = request.GET.get('club_id')
    selected_club = None
    if selected_club_id:
        selected_club = get_object_or_404(Club, id=selected_club_id)
    return render(request, 'activities/artistic.html', {'clubs': clubs, 'selected_club': selected_club})


def scientific_activities(request):
    clubs = Club.objects.filter(activity_type='scientific')
    selected_club_id = request.GET.get('club_id')
    selected_club = None
    if selected_club_id:
        selected_club = get_object_or_404(Club, id=selected_club_id)
    return render(request, 'activities/scientific.html', {'clubs': clubs, 'selected_club': selected_club})


def sports_activities(request):
    clubs = Club.objects.filter(activity_type='sports')
    selected_club_id = request.GET.get('club_id')
    selected_club = None
    if selected_club_id:
        selected_club = get_object_or_404(Club, id=selected_club_id)
    return render(request, 'activities/sports.html', {'clubs': clubs, 'selected_club': selected_club})


def club_detail(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    if club.activity_type == 'artistic':
        return artistic_activities(request)
    elif club.activity_type == 'scientific':
        return scientific_activities(request)
    elif club.activity_type == 'sports':
        return sports_activities(request)
    else:
        return redirect('home')


@login_required
def register_child(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    current_user = request.user
    if current_user.is_authenticated:
        parent, created = Parent.objects.get_or_create(user=current_user)
    else:
        return redirect('login')

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, parent=parent, club_id=club_id)
        print("Post duomenys:", request.POST)
        if form.is_valid():
            print("Forma yra teisinga. Valyti duomenys:", form.cleaned_data)
            form.save()
            print("Duomenys išsaugoti sėkmingai.")
            return redirect('registration_success')
        else:
            print("Forma yra neteisinga. Klaidos:", form.errors)
    else:
        form = EnrollmentForm(parent=parent, club_id=club_id)
    return render(request, 'enrollment/register_child.html', {'form': form, 'club': club})


def registration_success(request):
    return render(request, 'enrollment/registration_success.html')


@login_required
def admin_profile(request):
    if request.user.is_superuser:
        users = User.objects.all()
        clubs = Club.objects.all()
        return render(request, 'admin_profile.html', {'users': users, 'clubs': clubs})
    else:
        return redirect('my_profile')


def user_children(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    children = Child.objects.filter(parent=user.parent)
    return render(request, 'admin/user_children.html', {'user': user, 'children': children})


def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    children = user.parent.children.all()
    enrolled_clubs = Club.objects.filter(sessions__enrollments__child__in=children).distinct()
    return render(request, 'admin/user_detail.html', {'user': user, 'children': children, 'enrolled_clubs': enrolled_clubs})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = 'Nauja žinutė iš kontaktų formos'
            message = f'Vardas: {first_name}\n Pavardė: {last_name}\n El. paštas: {email}\n\n Žinutė: {message}'
            sender = settings.DEFAULT_FROM_EMAIL
            recipients = ['mmindaugass1992@gmail.com']

            send_mail(subject, message, sender, recipients)

            return render(request, 'contact/success.html')
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})


def success(request):
    return render(request, 'contact/success.html')


def generate_club_file(club):
    filename = f"{club.name}_info.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Club Name', 'Session', 'Child Name', 'Age', 'Parent Name', 'Email', 'Phone Number', 'Registration Date'])
        for session in club.sessions.all():
            for enrollment in session.enrollments.all():
                child = enrollment.child
                parent = child.parent
                writer.writerow([club.name, f"{session.day_of_week} {session.start_time}-{session.end_time} ({session.group})",
                                 f"{child.first_name} {child.last_name}", child.child_age,
                                 f"{parent.first_name} {parent.last_name}", parent.email, parent.phone_number,
                                 enrollment.registration_date])
    return filename


@login_required
def download_club_file(request, club_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    club = get_object_or_404(Club, id=club_id)
    filename = generate_club_file(club)
    with open(filename, 'rb') as file:
        response = HttpResponse(file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def user_list(request):
    users = User.objects.all()

    username = request.GET.get('username', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')

    if username:
        users = users.filter(username__icontains=username)
    if first_name:
        users = users.filter(parent__first_name__icontains=first_name)
    if last_name:
        users = users.filter(parent__last_name__icontains=last_name)

    return render(request, 'admin/user_list.html', {'users': users})


def download_all_club_files(request):
    clubs = Club.objects.all()
    return render(request, 'admin/download_all_club_files.html', {'clubs': clubs})


def children_list(request):
    children = Child.objects.all()

    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    age = request.GET.get('child_age', '')
    school = request.GET.get('school', '')
    classroom = request.GET.get('classroom', '')

    if first_name:
        children = children.filter(first_name__icontains=first_name)
    if last_name:
        children = children.filter(last_name__icontains=last_name)
    if age:
        children = children.filter(child_age=age)
    if school:
        children = children.filter(school__icontains=school)
    if classroom:
        children = children.filter(classroom__icontains=classroom)

    return render(request, 'admin/children_list.html', {'children': children})


def enrollment_list(request):
    search_query = request.GET.get('search_query')
    enrollments = Enrollment.objects.all()

    if search_query:
        enrollments = enrollments.filter(child__first_name__icontains=search_query) | \
                      enrollments.filter(child__last_name__icontains=search_query)

    return render(request, 'admin/enrollment_list.html', {'enrollments': enrollments})


@require_POST
def delete_enrollment(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    return render(request, 'admin/confirm_delete.html', {'enrollment': enrollment})


def confirm_delete(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    enrollment.delete()
    return redirect('enrollment_list')


def search(request):
    query = request.GET.get('q')
    clubs = Club.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'clubs': clubs, 'query': query})
