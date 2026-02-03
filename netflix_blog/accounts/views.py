from django.shortcuts import render
@login_required
def post_create_view(request):
    """Create new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
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
    """Edit post"""
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot edit this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
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
    """Delete post"""
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot delete this post.')
        return redirect('blog:post_detail', slug=slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted!')
        return redirect('blog:home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})
# Create your views here.
