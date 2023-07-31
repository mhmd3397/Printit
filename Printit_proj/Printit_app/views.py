from django.shortcuts import render, redirect
from .models import Idea, User, Comment, Star
from django.contrib import messages
import bcrypt


def home(request):
    # Get featured ideas with most stars
    featured_ideas_stars = Idea.objects.all().order_by('-star__stars')[:3]

    # Get featured ideas with most comments
    featured_ideas_comments = Idea.objects.all().order_by('-comment__id')[:3]

    # Combine and remove duplicates from the two querysets
    featured_ideas = (featured_ideas_stars | featured_ideas_comments)[:3]

    # Get featured users with most ideas
    featured_users_ideas = User.objects.all().order_by('-idea__id')[:3]

    # Get featured users with most comments
    featured_users_comments = User.objects.all().order_by('-comment__id')[:3]

    # Combine and remove duplicates from the two querysets
    featured_users = (featured_users_ideas | featured_users_comments)[:3]

    context = {
        'featured_ideas': featured_ideas,
        'featured_users': featured_users,
    }
    return render(request, 'home.html', context)


def register(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password']
        bio = request.POST.get('bio', '')  # Bio is optional

        # Basic validation
        errors = User.objects.basic_validator_registration(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('register')
        else:
            pw_hash = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()).decode()
            # Save the new user in the database
            user = User.objects.create(
                first_name=first_name, last_name=last_name, email=email, password=pw_hash, bio=bio)

            # Store the user's information in the session
            request.session['user'] = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'bio': user.bio,
            }
            # Redirect to the home page or any other page you want after successful registration
            return redirect('home')

    # If the request method is GET, display the registration form
    return render(request, 'register.html')


def login(request):
    # Implement user login logic here
    return render(request, 'login.html')


def create_idea(request):
    # Implement logic to create an idea here
    return render(request, 'create_idea.html')


def view_idea(request, idea_id):
    # Implement logic to fetch and display idea details here
    return render(request, 'view_idea.html', {'idea_id': idea_id})
