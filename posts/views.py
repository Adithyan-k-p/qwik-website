from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timesince import timesince
from django.utils import timezone
from .forms import PostForm
from accounts.models import User, Follow
from .models import Post, Like, Comment

@never_cache
@login_required
def home_view(request):
    posts = Post.objects.filter(is_active=True)\
                .annotate(
                    like_count=Count('likes', distinct=True),
                    comment_count=Count('comments', distinct=True)
                ).order_by('-created_at')
    
    liked_posts_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

    # Suggestions logic...
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

@login_required
def like_post_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    # Check if like exists
    like_filter = Like.objects.filter(user=request.user, post=post)
    
    if like_filter.exists():
        like_filter.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Count likes directly from the Like model to avoid IDE errors
        count = Like.objects.filter(post=post).count()
        return JsonResponse({
            'liked': liked,
            'like_count': count
        })
        
    return redirect(request.META.get('HTTP_REFERER', 'posts:home')) 

@login_required
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text:
            comment = Comment.objects.create(user=request.user, post=post, text=text)
            
            # This part prevents the reload!
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'username': comment.user.username,
                    'profile_url': reverse('accounts:profile', kwargs={'username': comment.user.username}),
                    'text': comment.text,
                })
    return redirect('posts:home')

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
def get_comments_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().select_related('user').order_by('-created_at')
    data = []
    for c in comments:
        data.append({
            'username': c.user.username,
            'text': c.text,
            'avatar': c.user.profile_image.url if c.user.profile_image else f"https://ui-avatars.com/api/?name={c.user.username}",
            'created_at': c.created_at.strftime("%b %d, %H:%M"),
            # Generate the profile URL
            'profile_url': reverse('accounts:profile', kwargs={'username': c.user.username})
        })
    return JsonResponse({'comments': data})

@login_required
def get_likes_ajax(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    likes = post.likes.all().select_related('user')
    data = []
    for l in likes:
        data.append({
            'username': l.user.username,
            'full_name': f"{l.user.first_name} {l.user.last_name}",
            'avatar': l.user.profile_image.url if l.user.profile_image else f"https://ui-avatars.com/api/?name={l.user.username}",
            # Generate the profile URL
            'profile_url': reverse('accounts:profile', kwargs={'username': l.user.username})
        })
    return JsonResponse({'likes': data})

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

@never_cache
@login_required
def explore_view(request):
    query = request.GET.get('q', '').strip()
    matched_users = None
    
    # 1. Base Query for Posts (Annotate counts for speed)
    posts_list = Post.objects.filter(visibility='public', is_active=True)\
        .annotate(
            like_count_attr=Count('likes', distinct=True),
            comment_count_attr=Count('comments', distinct=True)
        ).order_by('-created_at')

    # 2. Handle the "Search Results" (People + Posts)
    if query:
        # Get users matching search (Excluding admins)
        matched_users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query)
        ).exclude(is_staff=True).exclude(is_superuser=True)[:8]

        # Filter the posts grid by caption or the poster's username
        posts_list = posts_list.filter(
            Q(caption__icontains=query) | 
            Q(user__username__icontains=query)
        )

    # 3. Pagination
    paginator = Paginator(posts_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 4. AJAX for Infinite Scroll
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        posts_data = []
        for post in page_obj:
            posts_data.append({
                'id': post.id,
                'image_url': post.image.url,
                'like_count': post.like_count_attr,
                'comment_count': post.comment_count_attr,
            })
        return JsonResponse({'posts': posts_data, 'has_next': page_obj.has_next()})

    return render(request, 'posts/explore.html', {
        'posts': page_obj,
        'matched_users': matched_users,
        'query': query
    })

@login_required
def post_detail_ajax(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().select_related('user').order_by('-created_at')
    
    comments_data = []
    for c in comments:
        comments_data.append({
            'username': c.user.username,
            'text': c.text,
            'avatar': c.user.profile_image.url if c.user.profile_image else f"https://ui-avatars.com/api/?name={c.user.username}",
            'profile_url': reverse('accounts:profile', kwargs={'username': c.user.username})
        })

    return JsonResponse({
        'pk': post.pk,
        'username': post.user.username,
        'user_avatar': post.user.profile_image.url if post.user.profile_image else f"https://ui-avatars.com/api/?name={post.user.username}",
        'profile_url': reverse('accounts:profile', kwargs={'username': post.user.username}),
        'image_url': post.image.url,
        'caption': post.caption,
        'likes_count': post.likes.count(),
        'is_liked': post.likes.filter(user=request.user).exists(),
        'comments': comments_data,
        'created_at': timesince(post.created_at).upper(),
    })

@login_required
def delete_post_view(request, post_id):
    """ Soft delete: User archives the post """
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.user:
        post.is_archived = True
        post.is_active = False # Hide from feed
        post.deleted_by = None  # User deleted it, not admin
        post.deleted_at = timezone.now()
        post.deletion_reason = 'user_deleted'
        post.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

@login_required
def restore_post_view(request, post_id):
    """ Restore: User brings back the post """
    post = get_object_or_404(Post, pk=post_id)
    
    # Only allow restore if user owns the post AND user deleted it (not admin)
    if request.user == post.user and post.deleted_by is None:
        post.is_archived = False
        post.is_active = True # Show in feed again
        post.deleted_at = None
        post.deletion_reason = ''
        
        # Optional: Check if it was a temporary post that already expired
        # The save() method in models.py handles expiration logic, so we just save()
        post.save() 
        
        # If the save() method set it back to inactive (because time expired), warn frontend
        if not post.is_active:
             return JsonResponse({'status': 'expired', 'message': 'Post restored but has expired.'})

        return JsonResponse({'status': 'success'})
    
    # Post was deleted by admin, cannot restore
    return JsonResponse({'status': 'error', 'message': 'This post was deleted by admin and cannot be restored.'}, status=403)

# ... keep update_post_caption and delete_comment_view as they were ...
@login_required
def update_post_caption(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        if request.user == post.user:
            new_caption = request.POST.get('caption', '')
            post.caption = new_caption
            post.save()
            return JsonResponse({'status': 'success', 'new_caption': new_caption})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.user:
        comment.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=403)