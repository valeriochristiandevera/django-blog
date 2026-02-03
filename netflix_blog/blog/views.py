from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

def home_view(request):
    """Netflix-style homepage with hero and grid"""
    # Get featured post for hero banner
    featured_post = Post.objects.filter(
        status='published',
        is_featured=True
    ).first()
    
    # Get all other published posts
    posts = Post.objects.filter(
        status='published'
    ).exclude(
        id=featured_post.id if featured_post else None
    ).select_related('author', 'category')
    
    # Pagination
    paginator = Paginator(posts, 12)  # 12 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'featured_post': featured_post,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/home.html', context)

def post_detail_view(request, slug):
    """Post detail page"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Increment views
    post.views += 1
    post.save(update_fields=['views'])
    
    # Get comments
    comments = post.comments.filter(active=True).select_related('author')
    
    # Handle comment form
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('blog:post_detail', slug=slug)
    else:
        comment_form = CommentForm()
    
    # Get related posts
    related_posts = Post.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:4]
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)