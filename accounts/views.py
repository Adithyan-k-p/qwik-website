from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Count
from .forms import SignUpForm, LoginForm, EditProfileForm, CustomPasswordChangeForm
from .models import User, Follow
from posts.models import Post, Like, Comment
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
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
    
    # 1. Get Posts
    posts = Post.objects.filter(user=profile_user, is_active=True)\
                .annotate(
                    like_count_attr=Count('likes', distinct=True),
                    comment_count_attr=Count('comments', distinct=True)
                ).order_by('-created_at')

    # 2. Main Follow Button Logic (Top of profile)
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # 3. Get Counts
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()

    # 4. Get Actual Lists (User Objects) for the Modals
    # We get the 'Follow' objects, then we can access .follower or .following in template
    followers_relations = Follow.objects.filter(following=profile_user).select_related('follower')
    following_relations = Follow.objects.filter(follower=profile_user).select_related('following')

    # 5. List of User IDs that the *Logged-in User* is currently following
    # This is needed to decide whether to show "Follow" or "Following" next to names in the lists
    my_following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    
    # 6. SUGGESTIONS
    suggestions = User.objects.exclude(id=request.user.id) \
                              .exclude(id__in=my_following_ids) \
                              .exclude(is_superuser=True) \
                              .exclude(is_staff=True) \
                              .order_by('?')[:5]

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        
        'followers_relations': followers_relations, 
        'following_relations': following_relations,
        'my_following_ids': my_following_ids, 
        'suggestions': suggestions,
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

@login_required
def follow_user_view(request, username):
    user_to_toggle = get_object_or_404(User, username=username)
    status = ''
    
    if request.user != user_to_toggle:
        follow_record = Follow.objects.filter(follower=request.user, following=user_to_toggle).first()
        if follow_record:
            follow_record.delete()
            status = 'unfollowed'
        else:
            Follow.objects.create(follower=request.user, following=user_to_toggle)
            status = 'followed'

    # --- AJAX RESPONSE ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        new_following_count = Follow.objects.filter(follower=request.user).count()
        
        # Prepare data for Dynamic List Injection
        avatar_url = "https://ui-avatars.com/api/?name=" + user_to_toggle.username
        if user_to_toggle.profile_image:
            avatar_url = user_to_toggle.profile_image.url
            
        full_name = f"{user_to_toggle.first_name} {user_to_toggle.last_name}".strip()
        
        return JsonResponse({
            'status': status, 
            'new_following_count': new_following_count,
            'username': user_to_toggle.username,
            'full_name': full_name,
            'avatar_url': avatar_url,
            'profile_url': f"/accounts/profile/{user_to_toggle.username}/" # Hardcoded url pattern for JS
        })

    # Standard Redirect
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('accounts:profile', username=username)


@login_required
def remove_follower_view(request, username):
    user_to_remove = get_object_or_404(User, username=username)
    
    # Check if a follow record exists where:
    # Follower = user_to_remove
    # Following = request.user (Me)
    follow_record = Follow.objects.filter(follower=user_to_remove, following=request.user).first()
    
    if follow_record:
        follow_record.delete()

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)

    return redirect('accounts:profile', username=request.user.username)

@login_required
def search_users_ajax(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'users': []})

    # Search users, exclude admins/staff and yourself
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query)
    ).exclude(is_staff=True).exclude(is_superuser=True).exclude(id=request.user.id)[:5]

    results = []
    for user in users:
        results.append({
            'username': user.username,
            'avatar': user.profile_image.url if user.profile_image else f"https://ui-avatars.com/api/?name={user.username}",
            'profile_url': f"/accounts/profile/{user.username}/"
        })
    
    return JsonResponse({'users': results})

@never_cache
@login_required
def settings_view(request):
    user = request.user
    
    # Initialize the form (GET request)
    password_form = CustomPasswordChangeForm(user)

    if request.method == 'POST':
        
        # --- 1. HANDLE PASSWORD CHANGE ---
        if 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                # Update session so user isn't logged out
                update_session_auth_hash(request, user)
                
                # Success Alert (Green)
                messages.success(request, 'Your password has been changed successfully!')
                return redirect('accounts:settings')
            else:
                # Error Alert (Red)
                # Loop through errors to display the specific backend validation failure
                if password_form.errors:
                    for field, errors in password_form.errors.items():
                        for error in errors:
                            messages.error(request, str(error))
                            break 
                        break
        
        # --- 2. HANDLE PRIVACY TOGGLE ---
        elif 'update_privacy' in request.POST:
            is_private = request.POST.get('is_private') == 'on'
            
            if user.is_private != is_private:
                user.is_private = is_private
                user.save()
                status_msg = "Private" if is_private else "Public"
                messages.success(request, f'Your account is now {status_msg}.')
            
            return redirect('accounts:settings')

    # --- FETCH DATA FOR TABS ---
    
    # 1. My Active Posts
    my_posts = Post.objects.filter(user=user, is_active=True, is_archived=False)\
                           .order_by('-created_at')

    # 2. Recycle Bin
    archived_posts = Post.objects.filter(user=user, is_archived=True)\
                                 .order_by('-created_at')

    # 3. Liked Posts
    my_likes = Like.objects.filter(user=user, post__is_active=True)\
                           .select_related('post', 'post__user')\
                           .order_by('-created_at')

    # 4. My Comments
    my_comments = Comment.objects.filter(user=user, post__is_active=True)\
                                 .select_related('post', 'post__user')\
                                 .order_by('-created_at')

    context = {
        'password_form': password_form,
        'my_posts': my_posts,
        'archived_posts': archived_posts,
        'my_likes': my_likes,
        'my_comments': my_comments,
        'active_tab': request.GET.get('tab', 'general') 
    }
    return render(request, 'accounts/settings.html', context)