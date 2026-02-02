from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone
from .decorators import admin_required
from accounts.models import User
from posts.models import Post, Comment
from reports.models import UserReport, PostReport
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
    
    # New: Report Statistics
    pending_reports = UserReport.objects.filter(status='pending').count() + PostReport.objects.filter(status='pending').count()
    resolved_reports = UserReport.objects.filter(status='resolved').count() + PostReport.objects.filter(status='resolved').count()
    
    new_users = User.objects.order_by('-created_at')[:5]

    context = {
        'total_users': total_users,
        'total_posts': total_posts,
        'flagged_posts': flagged_posts,
        'banned_users': banned_users,
        'total_comments': total_comments,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'new_users': new_users
    }
    return render(request, 'custom_admin/dashboard.html', context)

@never_cache
@admin_required
def users_list(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    
    # Annotate with report count
    users = User.objects.annotate(
        report_count=Count('reports_received')
    ).order_by('-created_at')

    # Filtering
    if filter_type == 'banned':
        users = users.filter(is_active=False)
    elif filter_type == 'active':
        users = users.filter(is_active=True)
    elif filter_type == 'admin':
        users = users.filter(role='admin')
    elif filter_type == 'reported':
        users = users.filter(report_count__gt=0)

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
    
    # Annotate with report count
    posts = Post.objects.select_related('user').annotate(
        report_count=Count('reports')
    ).order_by('-created_at')

    # Filtering
    if filter_type == 'live':
        posts = posts.filter(is_active=True, is_archived=False)
    elif filter_type == 'archived':
        posts = posts.filter(is_archived=True) # Soft Deleted
    elif filter_type == 'flagged':
        posts = posts.filter(is_flagged=True) # NSFW
    elif filter_type == 'reported':
        posts = posts.filter(report_count__gt=0)

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


# ============= REPORTS MANAGEMENT =============

@never_cache
@admin_required
def reports_list(request):
    """View all reports (User & Post) with filters and actions"""
    report_type = request.GET.get('type', 'all')  # all, user, post
    status_filter = request.GET.get('status', 'all')  # all, pending, reviewed, resolved, dismissed
    reason_filter = request.GET.get('reason', 'all')
    query = request.GET.get('q', '')
    
    # Get ALL reports first (for total count)
    all_user_reports = UserReport.objects.select_related('reporter', 'reported_user').all()
    all_post_reports = PostReport.objects.select_related('reporter', 'post', 'post__user').all()
    
    # Combine both report types for counting
    all_total_reports = list(all_user_reports) + list(all_post_reports)
    
    # Now apply filters for display
    user_reports = UserReport.objects.select_related('reporter', 'reported_user').all()
    post_reports = PostReport.objects.select_related('reporter', 'post', 'post__user').all()
    
    # Filter by type
    if report_type == 'user':
        post_reports = PostReport.objects.none()
    elif report_type == 'post':
        user_reports = UserReport.objects.none()
    
    # Filter by status
    if status_filter != 'all':
        user_reports = user_reports.filter(status=status_filter)
        post_reports = post_reports.filter(status=status_filter)
    
    # Filter by reason
    if reason_filter != 'all':
        user_reports = user_reports.filter(reason=reason_filter)
        post_reports = post_reports.filter(reason=reason_filter)
    
    # Search in description
    if query:
        user_reports = user_reports.filter(
            Q(description__icontains=query) | 
            Q(reported_user__username__icontains=query)
        )
        post_reports = post_reports.filter(
            Q(description__icontains=query) | 
            Q(post__caption__icontains=query)
        )
    
    # Combine and order
    all_reports = list(user_reports) + list(post_reports)
    all_reports.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate stats for ALL reports (not filtered)
    total_all_reports = len(all_total_reports)
    pending_all = sum(1 for r in all_total_reports if r.status == 'pending')
    reviewed_all = sum(1 for r in all_total_reports if r.status == 'reviewed')
    
    # Calculate stats for FILTERED reports
    total_filtered = len(all_reports)
    pending_filtered = sum(1 for r in all_reports if r.status == 'pending')
    reviewed_filtered = sum(1 for r in all_reports if r.status == 'reviewed')
    
    if is_ajax(request):
        html = render_to_string('custom_admin/partials/report_rows.html', {'reports': all_reports}, request=request)
        return HttpResponse(html)
    
    context = {
        'user_reports': user_reports,
        'post_reports': post_reports,
        'all_reports': all_reports,
        'total_reports': total_all_reports,  # Always show total of ALL reports
        'pending_count': pending_all,  # Always show total pending of ALL reports
        'reviewed_count': reviewed_all,  # Always show total reviewed of ALL reports
        'report_type': report_type,
        'status_filter': status_filter,
    }
    return render(request, 'custom_admin/reports.html', context)


@never_cache
@admin_required
def update_report_status(request, report_id, report_type):
    """Update report status (pending, reviewed, resolved, dismissed)"""
    new_status = request.POST.get('status')
    
    if report_type == 'user':
        report = get_object_or_404(UserReport, pk=report_id)
    else:
        report = get_object_or_404(PostReport, pk=report_id)
    
    if new_status in ['pending', 'reviewed', 'resolved', 'dismissed']:
        report.status = new_status
        report.save()
        messages.success(request, f"Report marked as {new_status.title()}.")
    
    return redirect('custom_admin:reports_list')


@never_cache
@admin_required
def view_user_report(request, report_id):
    """View detailed user report"""
    report = get_object_or_404(UserReport, pk=report_id)
    context = {
        'report': report,
        'report_type': 'user',
    }
    return render(request, 'custom_admin/report_detail.html', context)


@never_cache
@admin_required
def view_post_report(request, report_id):
    """View detailed post report"""
    report = get_object_or_404(PostReport, pk=report_id)
    context = {
        'report': report,
        'report_type': 'post',
    }
    return render(request, 'custom_admin/report_detail.html', context)


@never_cache
@admin_required
@admin_required
@never_cache
def post_detail_admin(request, post_id):
    """Admin endpoint to view post details (simplified - image, caption, username only)"""
    from django.http import JsonResponse
    
    try:
        post = Post.objects.get(pk=post_id)
        return JsonResponse({
            'username': post.user.username,
            'image_url': post.image.url if post.image else '',
            'caption': post.caption or '(No caption)',
        })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)