from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Post
from .forms import PostForm

@never_cache
@login_required
def home_view(request):
    # Fetch all posts, ordered by newest first
    # In the future, you can filter this to only show followed users
    # posts = Post.objects.all().order_by('-created_at')
    posts = Post.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'posts': posts
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