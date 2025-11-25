from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .forms import PostForm
from accounts.models import User, Follow
from .models import Post, Like, Comment

@never_cache
@login_required
def home_view(request):
    # Fetch all posts, ordered by newest first
    # In the future, you can filter this to only show followed users
    # posts = Post.objects.all().order_by('-created_at')
    posts = Post.objects.filter(is_active=True).order_by('-created_at')
    
    # Get IDs of posts liked by user
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    # Get IDs of users the current user follows
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

    # Get Suggestions (The same logic used in Profile View)
    # Exclude self, existing follows, admins, and staff
    suggestions = User.objects.exclude(id=request.user.id) \
                              .exclude(id__in=following_ids) \
                              .exclude(is_superuser=True) \
                              .exclude(is_staff=True) \
                              .order_by('?')[:5]
    
    context = {
        'posts': posts,
        'liked_posts_ids': liked_posts_ids,
        'following_ids': following_ids,
        'suggestions': suggestions, 
    }
    return render(request, 'posts/home.html', context)

@never_cache
@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES) 
        
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.media_type = 'image' # Force type
            
            post.save()
            
            return redirect('posts:home')
        else:
            print(form.errors) # Print errors to terminal if upload fails
    else:
        form = PostForm(initial={
            'media_type': 'image', 
            'post_type': 'temporary',
            'visibility': 'public' 
        })

    return render(request, 'posts/create.html', {'form': form})

@never_cache
@login_required
def like_post_view(request, post_id):
    # Change 'id=post_id' to 'pk=post_id'
    post = get_object_or_404(Post, pk=post_id) 
    
    like = Like.objects.filter(user=request.user, post=post).first()
    if like:
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
        
    return redirect(request.META.get('HTTP_REFERER', 'posts:home'))

@never_cache
@login_required
def add_comment_view(request, post_id):
    # Change 'id=post_id' to 'pk=post_id'
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text:
            Comment.objects.create(user=request.user, post=post, text=text)
            
    return redirect(request.META.get('HTTP_REFERER', 'posts:home'))

@login_required
def profile_view(request, username):
    # 1. Get the Profile User
    profile_user = get_object_or_404(User, username=username)
    
    # 2. Check if I am following them
    # We use .exists() which returns True or False
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    # 3. Get Counts (use Follow model queries instead of relying on reverse relation names)
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    
    # 4. Get Posts
    posts = Post.objects.filter(user=profile_user, is_active=True).order_by('-created_at')

    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,      # Passed to template
        'followers_count': followers_count, # Passed to template
        'following_count': following_count, # Passed to template
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def follow_user_view(request, username):
    user_to_toggle = get_object_or_404(User, username=username)
    
    if request.user != user_to_toggle:
        follow_record = Follow.objects.filter(follower=request.user, following=user_to_toggle).first()
        
        if follow_record:
            follow_record.delete()
            status = 'unfollowed'
        else:
            Follow.objects.create(follower=request.user, following=user_to_toggle)
            status = 'followed'
        # --- NEW: AJAX Support ---
        # If the request comes from JavaScript (fetch), return JSON data
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            new_count = Follow.objects.filter(following=user_to_toggle).count()
            return JsonResponse({
                'status': status, 
                'new_count': new_count
            })
            
    # Fallback for non-JS browsers (Standard Reload)
    return redirect('accounts:profile', username=username)