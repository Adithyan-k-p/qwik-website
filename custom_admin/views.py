from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from .decorators import admin_required
from accounts.models import User
from posts.models import Post, Comment
from django.views.decorators.cache import never_cache

# --- Helper for AJAX ---
def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'
@never_cache
@admin_required
def dashboard_view(request):
    total_users = User.objects.count()
    total_posts = Post.objects.filter(is_active=True).count()
    flagged_posts = Post.objects.filter(is_flagged=True).count()
    banned_users = User.objects.filter(is_active=False).count()
    total_comments = Comment.objects.count()
    
    new_users = User.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'flagged_posts': flagged_posts,
        'banned_users': banned_users,
        'total_comments': total_comments,
        'new_users': new_users
    }
    return render(request, 'custom_admin/dashboard.html', context)

@never_cache
@admin_required
def users_list(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    users = User.objects.all().order_by('-created_at')

    # Filtering
    if filter_type == 'banned':
        users = users.filter(is_active=False)
    elif filter_type == 'active':
        users = users.filter(is_active=True)
    elif filter_type == 'admin':
        users = users.filter(role='admin')

    # Search
    if query:
        users = users.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)
        )

    # AJAX Response for Realtime Search
    if is_ajax(request):
        html = render_to_string('custom_admin/partials/user_rows.html', {'users': users}, request=request)
        return HttpResponse(html)

    return render(request, 'custom_admin/users.html', {'users': users})

@never_cache
@admin_required
def ban_user_with_remark(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        if user == request.user:
            messages.error(request, "Cannot ban yourself.")
            return redirect('custom_admin:users_list')

        # Save Note
        note = request.POST.get('admin_note')
        if note:
            user.admin_notes = note
        
        # Toggle Ban
        user.is_active = not user.is_active
        user.save()
        
        status = "Banned" if not user.is_active else "Unbanned"
        messages.success(request, f"User {status}. Remark updated.")
        
    return redirect('custom_admin:users_list')

@never_cache
@admin_required
def posts_list(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'live')
    
    posts = Post.objects.select_related('user').order_by('-created_at')

    # Filtering
    if filter_type == 'live':
        posts = posts.filter(is_active=True, is_archived=False)
    elif filter_type == 'archived':
        posts = posts.filter(is_archived=True) # Soft Deleted
    elif filter_type == 'flagged':
        posts = posts.filter(is_flagged=True) # NSFW

    if query:
        posts = posts.filter(
            Q(caption__icontains=query) | 
            Q(user__username__icontains=query)
        )

    if is_ajax(request):
        html = render_to_string('custom_admin/partials/post_rows.html', {'posts': posts}, request=request)
        return HttpResponse(html)

    return render(request, 'custom_admin/posts.html', {'posts': posts})

@never_cache
@admin_required
def flag_post(request, post_id):
    """ Mark as NSFW/Flagged """
    post = get_object_or_404(Post, pk=post_id)
    post.is_flagged = not post.is_flagged
    post.save()
    
    msg = "Post Flagged as NSFW" if post.is_flagged else "Post Unflagged"
    messages.success(request, msg)
    return redirect('custom_admin:posts_list')

@never_cache
@admin_required
@never_cache
@admin_required
def delete_post(request, post_id):
    """ Soft Delete / Restore """
    post = get_object_or_404(Post, pk=post_id)
    if post.is_archived:
        # Restore
        post.is_archived = False
        post.is_active = True
        post.deleted_by = None
        post.deleted_at = None
        post.deletion_reason = ''
        messages.success(request, "Post Restored.")
    else:
        # Soft Delete (Admin)
        post.is_archived = True
        post.is_active = False
        post.deleted_by = request.user  # Track that admin deleted it
        post.deleted_at = timezone.now()
        post.deletion_reason = 'admin_deleted'
        messages.success(request, "Post Moved to Archive.")
    post.save()
    return redirect('custom_admin:posts_list')

@never_cache
@admin_required
def comments_list(request):
    query = request.GET.get('q', '')
    comments = Comment.objects.select_related('user', 'post').order_by('-created_at')
    
    if query:
        comments = comments.filter(text__icontains=query)
        
    if is_ajax(request):
        html = render_to_string('custom_admin/partials/comment_rows.html', {'comments': comments}, request=request)
        return HttpResponse(html)

    return render(request, 'custom_admin/comments.html', {'comments': comments})

@never_cache
@admin_required
def delete_comment(request, comment_id):
    """Delete/Remove inappropriate comments"""
    comment = get_object_or_404(Comment, pk=comment_id)
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect('custom_admin:comments_list')

@never_cache
@admin_required
def change_password(request):
    """Change admin password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate old password
        if not request.user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return redirect('custom_admin:change_password')
        
        # Check new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('custom_admin:change_password')
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('custom_admin:change_password')
        
        # Check new password is different from old
        if old_password == new_password:
            messages.error(request, "New password must be different from old password.")
            return redirect('custom_admin:change_password')
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        messages.success(request, "Password changed successfully!")
        return redirect('custom_admin:dashboard')
    
    return render(request, 'custom_admin/change_password.html')