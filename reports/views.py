from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import PostReport, UserReport
from accounts.models import User
from posts.models import Post

@login_required
@require_POST
def submit_report(request):
    target_type = request.POST.get('target_type') # 'post' or 'user'
    target_id = request.POST.get('target_id')
    reason = request.POST.get('reason')
    description = request.POST.get('description', '')

    if not reason or not target_id:
        return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

    try:
        if target_type == 'post':
            post_obj = get_object_or_404(Post, pk=target_id)
            # Create PostReport
            PostReport.objects.create(
                reporter=request.user,
                post=post_obj,
                reason=reason,
                description=description
            )
            
        elif target_type == 'user':
            user_obj = get_object_or_404(User, pk=target_id)
            
            if user_obj == request.user:
                 return JsonResponse({'status': 'error', 'message': 'You cannot report yourself.'}, status=400)

            # Create UserReport
            UserReport.objects.create(
                reporter=request.user,
                reported_user=user_obj,
                reason=reason,
                description=description
            )
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid target type'}, status=400)

        return JsonResponse({'status': 'success', 'message': 'Report submitted successfully.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)