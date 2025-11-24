from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, EditProfileForm
from .models import User
from posts.models import Post 
from django.views.decorators.cache import never_cache
import os

def check_username(request):
    username = request.GET.get('username', '').strip().lower()
    data = {'is_taken': False}
    
    if username and User.objects.filter(username__iexact=username).exists():
        data['is_taken'] = True
        
    return JsonResponse(data)

def check_email(request):
    email = request.GET.get('email', '').strip().lower()
    data = {'is_taken': False}
    
    if email and User.objects.filter(email__iexact=email).exists():
        data['is_taken'] = True
        
    return JsonResponse(data)


# def check_username(request):
#     username = request.GET.get('username', None)
#     current_user = request.user.username
    
#     data = {
#         'is_taken': False
#     }
    
#     # If user types their own name, it's not "taken"
#     if username and username.lower() != current_user.lower():
#         if User.objects.filter(username__iexact=username).exists():
#             data['is_taken'] = True
            
#     return JsonResponse(data)

@never_cache
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('posts:home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@never_cache
def login_view(request):
    if request.method == 'POST':
        # form = AuthenticationForm(request, data=request.POST)
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('posts:home')
    else:
        # form = AuthenticationForm()
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('accounts:login')

@never_cache
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # --- FIX HERE: Change 'author' to 'user' ---
    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'posts': user_posts,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def current_profile_redirect(request):
    # If a user goes to /accounts/profile/, redirect them to /accounts/profile/their_username/
    return redirect('accounts:profile', username=request.user.username)


@never_cache
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            # 1. Get the flags
            delete_old_image = form.cleaned_data.get('remove_image')
            new_image_uploaded = 'profile_image' in request.FILES
            
            # 2. Handle File Deletion (Remove from Disk)
            if delete_old_image or new_image_uploaded:
                try:
                    # Fetch fresh instance to get the current file path
                    current_db_user = User.objects.get(pk=request.user.pk)
                    if current_db_user.profile_image:
                        old_path = current_db_user.profile_image.path
                        if os.path.exists(old_path):
                            os.remove(old_path)
                except Exception as e:
                    print(f"Error deleting file: {e}")

            # 3. Prepare User Object
            user = form.save(commit=False)
            
            # 4. Handle Database Field Clearing
            # If user clicked remove, and didn't immediately upload a replacement
            if delete_old_image and not new_image_uploaded:
                user.profile_image = None 
                
            user.save()
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})