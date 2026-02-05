from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
def home_view(request):
    """Homepage showing published posts"""
    posts = Post.objects.filter(
        status='published'
    ).select_related('author', 'category')
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/home.html', context)
def post_detail_view(request, slug):
    """Individual post detail with comments"""
    post = get_object_or_404(Post, slug=slug, status='published')
    # Increment views
    post.views += 1
    post.save(update_fields=['views'])
    # Get comments
    comments = post.comments.filter(active=True).select_related('author')
    # Handle comment submission
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
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)
@login_required
def post_create_view(request):
    """Create a new blog post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'action': 'Create'
    })
@login_required
def post_edit_view(request, slug):
    """Edit existing blog post"""
    post = get_object_or_404(Post, slug=slug)
    # Permission check
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot edit this post.')
        return redirect('blog:post_detail', slug=slug)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.status == 'published' and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'Post updated!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {
        'form': form, 
        'action': 'Edit', 
        'post': post
    })
@login_required
def post_delete_view(request, slug):
    """Delete blog post"""
    post = get_object_or_404(Post, slug=slug)
    # Permission check
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot delete this post.')
        return redirect('blog:post_detail', slug=slug)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted!')
        return redirect('blog:home')
    return render(request, 'blog/post_confirm_delete.html', {'post': post})