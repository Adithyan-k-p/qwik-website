from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Check if user role is admin OR superuser
        if request.user.role == 'admin' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, "Access Denied: Admins only.")
        return redirect('posts:home')
    return _wrapped_view