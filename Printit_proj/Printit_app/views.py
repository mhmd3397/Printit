from django.shortcuts import render, redirect
from .models import Idea, User, Comment, Star
from django.contrib import messages
import bcrypt


def home(request):
    # Check if the user is logged in (authenticated)
    if 'user' in request.session:
        return redirect('home_authenticated')
    else:
        # If the user is not logged in, display the regular home page
        featured_ideas_stars = Idea.objects.all().order_by('-star__stars')[:3]
        featured_ideas_comments = Idea.objects.all().order_by(
            '-comment__id')[:3]
        featured_ideas = (featured_ideas_stars | featured_ideas_comments)[:3]
        featured_users_ideas = User.objects.all().order_by('-idea__id')[:3]
        featured_users_comments = User.objects.all().order_by(
            '-comment__id')[:3]
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
    if request.method == 'POST':
        # Get form data
        email = request.POST['email']

        # Check if the email exists in the database
        user = User.objects.filter(email=email).first()
        # Basic validation
        errors = User.objects.basic_validator_login(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('register')
        else:
            # Store the user's information in the session
            user = User.objects.get(email=email)
            request.session['user'] = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'bio': user.bio,
            }
            # Redirect to the home page or any other page you want after successful login
            return redirect('home')

    # If the request method is GET, display the login form
    return render(request, 'login.html')


def home_authenticated(request):
    # Get the user details from the session
    user_id = request.session['user']['id']
    user = User.objects.get(pk=user_id)

    # Fetch user-specific data for the home page (you can customize this based on your needs)
    # For example, you can get the user's own ideas, starred ideas, etc.
    user_ideas = Idea.objects.filter(user=user).order_by('-created_at')[:3]
    starred_ideas = Idea.objects.filter(
        star__user=user).order_by('-created_at')[:3]

    context = {
        'user_ideas': user_ideas,
        'starred_ideas': starred_ideas,
        'user': user
    }

    return render(request, 'home_authenticated.html', context)


def my_ideas(request):
    # Check if the user is logged in (authenticated)
    if 'user' in request.session:
        # Get the user details from the session
        user_id = request.session['user']['id']
        user = User.objects.get(pk=user_id)

        # Fetch the ideas created by the current user
        user_ideas = Idea.objects.filter(user=user).order_by('-created_at')

        context = {
            'user_ideas': user_ideas,
            'user': user
        }

        return render(request, 'my_ideas.html', context)
    else:
        # If the user is not logged in, redirect to the login page or any other page you want
        return redirect('login')


def create_idea(request):
    if 'user' not in request.session:
        # Redirect to login page or home page if the user is not authenticated
        return redirect('home')

    if request.method == 'POST':
        # Get form data
        title = request.POST['title']
        content = request.POST['content']
        user_id = request.session['user']['id']

        # Validate the idea data
        errors = Idea.objects.basic_validator_idea(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('create_idea')

        # Create the new idea
        user = User.objects.get(pk=user_id)
        idea = Idea.objects.create(user=user, title=title, content=content)
        context = {
            'user': user
        }
        # Redirect to the view idea page for the newly created idea
        return redirect('view_idea', idea_id=idea.id)
    # If the request method is GET, display the create idea form
    return render(request, 'create_idea.html')


def view_idea(request, idea_id):
    # Get the idea and its details
    idea = Idea.objects.get(pk=idea_id)

    # Get comments for the idea
    comments = Comment.objects.filter(idea=idea)

    # Calculate the number of comments
    comments_count = comments.count()

    # Calculate the average star rating for the idea

    context = {
        'idea': idea,
        'comments': comments,
        'comments_count': comments_count,
    }
    return render(request, 'view_idea_with_comments.html', context)


def user_ideas(request, user_id):
    # Get the user and their ideas
    user = User.objects.get(pk=user_id)
    user_ideas = Idea.objects.filter(user=user).order_by('-created_at')

    context = {
        'user': user,
        'user_ideas': user_ideas,
    }
    return render(request, 'user_ideas.html', context)


def edit_idea(request, idea_id):
    if 'user' not in request.session:
        return redirect('home')

    try:
        idea = Idea.objects.get(pk=idea_id)
    except Idea.DoesNotExist:
        messages.error(request, 'Idea not found.')
        return redirect('my_ideas')

    if request.method == 'POST':
        # Get form data
        title = request.POST['title']
        content = request.POST['content']

        # Use the IdeaManager's basic_validator_idea for form validation
        errors = Idea.objects.basic_validator_idea(request.POST)
        if errors:
            # If there are errors, display them as messages and render the form again with the entered data
            for key, value in errors.items():
                messages.error(request, value)
            context = {
                'idea': idea,
                'title': title,
                'content': content,
            }
            return render(request, 'edit_idea.html', context)
        else:
            # If there are no errors, update the idea in the database
            idea.title = title
            idea.content = content
            idea.save()
            # Redirect to the view idea page for the updated idea
            return redirect('view_idea', idea_id=idea.id)

    # If the request method is GET, display the edit idea form with the idea data
    context = {
        'idea': idea,
        'title': idea.title,
        'content': idea.content,
    }
    return render(request, 'edit_idea.html', context)


def delete_idea(request, idea_id):
    if 'user' not in request.session:
        return redirect('home')

    try:
        idea = Idea.objects.get(pk=idea_id)
    except Idea.DoesNotExist:
        messages.error(request, 'Idea not found.')
        return redirect('my_ideas')

    if request.method == 'POST':
        # Delete the idea from the database
        idea.delete()
        # Redirect to the my_ideas page or any other page you want after successful deletion
        return redirect('my_ideas')

    # If the request method is GET, display the delete idea confirmation page
    context = {
        'idea': idea,
    }
    return render(request, 'delete_idea.html', context)


def logout(request):
    # Clear the user's session and log them out
    request.session.flush()

    # Redirect the user to the home page or any other page you want after logout
    return redirect('home')
