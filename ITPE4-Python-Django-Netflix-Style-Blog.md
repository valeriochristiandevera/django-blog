# Django Netflix-Style Blog Project
## Complete Guide for All Groups

Build a modern, Netflix-inspired blog platform with Django.

---

## 🎯 Project Overview

**What You're Building:**
A sleek, dark-themed blog platform inspired by Netflix's design with:
- Hero banner with featured post
- Card-based post grid layout
- Smooth hover effects
- Dark theme with accent colors
- User authentication
- Full CRUD operations

**Key Features:**
- ✅ User Registration & Login
- ✅ Create/Edit/Delete Blog Posts
- ✅ Comment System
- ✅ Categories
- ✅ Featured Posts (like Netflix hero banner)
- ✅ Dark Theme UI
- ✅ Responsive Design

---

## 📁 Project Structure

```
netflix_blog/
├── manage.py
├── netflix_blog/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── blog/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   └── blog/
│       ├── home.html
│       ├── post_detail.html
│       └── post_form.html
└── static/
    ├── css/
    │   └── netflix.css
    └── js/
        └── main.js
```

---

## 🎨 Design Specifications

### Color Scheme
```css
Primary Background: #141414 (Netflix black)
Secondary Background: #1a1a1a
Accent Red: #E50914 (Netflix red)
Text White: #ffffff
Text Gray: #808080
Card Background: #2a2a2a
Hover Effect: #3a3a3a
```

### Typography
- Font Family: 'Helvetica Neue', Arial, sans-serif
- Hero Title: 48px, Bold
- Post Title: 24px, Bold
- Body Text: 16px, Regular
- Small Text: 14px, Regular

### Layout
- Hero Banner: Full width, 70vh height
- Post Cards: 300px x 400px
- Card Grid: 4 columns on desktop, 2 on tablet, 1 on mobile
- Max Container Width: 1400px
- Padding/Margins: 20px standard

---

## 🗄️ Database Models

### 1. CustomUser Model
```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return self.username
```

### 2. Category Model
```python
# blog/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

### 3. Post Model
```python
class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
    )
    is_featured = models.BooleanField(default=False)  # For hero banner
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:297] + '...'
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
```

### 4. Comment Model
```python
class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
```

---

## 🎬 Views Implementation

### Blog Views
```python
# blog/views.py
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
```

---

## 🎨 Netflix-Style CSS

```css
/* static/css/netflix.css */

/* Reset and Base */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    background-color: #141414;
    color: #ffffff;
    line-height: 1.6;
}

/* Navigation */
.navbar {
    background-color: #141414;
    padding: 20px 4%;
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid #2a2a2a;
}

.navbar-brand {
    color: #E50914;
    font-size: 32px;
    font-weight: bold;
    text-decoration: none;
}

.nav-links {
    display: flex;
    gap: 30px;
    list-style: none;
}

.nav-links a {
    color: #ffffff;
    text-decoration: none;
    font-size: 16px;
    transition: color 0.3s;
}

.nav-links a:hover {
    color: #E50914;
}

/* Hero Banner */
.hero-banner {
    height: 70vh;
    background-size: cover;
    background-position: center;
    position: relative;
    margin-top: 70px;
    display: flex;
    align-items: flex-end;
}

.hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        to top,
        rgba(20, 20, 20, 1) 0%,
        rgba(20, 20, 20, 0.4) 60%,
        rgba(20, 20, 20, 0.8) 100%
    );
}

.hero-content {
    position: relative;
    z-index: 2;
    padding: 60px 4%;
    max-width: 600px;
}

.hero-title {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: 20px;
}

.hero-description {
    font-size: 18px;
    color: #ffffff;
    margin-bottom: 30px;
    line-height: 1.6;
}

.hero-buttons {
    display: flex;
    gap: 15px;
}

.btn-play,
.btn-info {
    padding: 12px 30px;
    font-size: 16px;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
    display: inline-block;
}

.btn-play {
    background-color: #ffffff;
    color: #000000;
}

.btn-play:hover {
    background-color: rgba(255, 255, 255, 0.75);
}

.btn-info {
    background-color: rgba(109, 109, 110, 0.7);
    color: #ffffff;
}

.btn-info:hover {
    background-color: rgba(109, 109, 110, 0.4);
}

/* Posts Grid */
.posts-section {
    padding: 60px 4%;
}

.section-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 30px;
    color: #ffffff;
}

.posts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

/* Post Card */
.post-card {
    background-color: #2a2a2a;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
    cursor: pointer;
}

.post-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.8);
}

.post-card-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.post-card-body {
    padding: 20px;
}

.post-card-title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #ffffff;
    text-decoration: none;
}

.post-card-title:hover {
    color: #E50914;
}

.post-card-meta {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    color: #808080;
    margin-bottom: 10px;
}

.post-card-excerpt {
    font-size: 14px;
    color: #b3b3b3;
    line-height: 1.5;
}

/* Category Badge */
.category-badge {
    background-color: #E50914;
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    text-decoration: none;
    display: inline-block;
}

/* Post Detail */
.post-detail {
    max-width: 900px;
    margin: 100px auto 60px;
    padding: 0 20px;
}

.post-detail-image {
    width: 100%;
    height: 500px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 30px;
}

.post-detail-title {
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 20px;
}

.post-detail-meta {
    display: flex;
    gap: 20px;
    color: #808080;
    margin-bottom: 30px;
    font-size: 14px;
}

.post-detail-content {
    font-size: 18px;
    line-height: 1.8;
    color: #e5e5e5;
    margin-bottom: 60px;
}

/* Comments */
.comments-section {
    border-top: 1px solid #2a2a2a;
    padding-top: 40px;
}

.comment {
    background-color: #2a2a2a;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.comment-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.comment-author {
    font-weight: bold;
    color: #ffffff;
}

.comment-date {
    color: #808080;
    font-size: 14px;
}

.comment-content {
    color: #e5e5e5;
    line-height: 1.6;
}

/* Forms */
.form-container {
    max-width: 600px;
    margin: 100px auto;
    padding: 40px;
    background-color: #2a2a2a;
    border-radius: 8px;
}

.form-group {
    margin-bottom: 25px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #ffffff;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 12px;
    background-color: #1a1a1a;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    color: #ffffff;
    font-size: 16px;
}

.form-control:focus {
    outline: none;
    border-color: #E50914;
}

textarea.form-control {
    min-height: 150px;
    resize: vertical;
}

/* Buttons */
.btn {
    padding: 12px 30px;
    font-size: 16px;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;
    display: inline-block;
}

.btn-primary {
    background-color: #E50914;
    color: #ffffff;
}

.btn-primary:hover {
    background-color: #b20710;
}

.btn-secondary {
    background-color: #3a3a3a;
    color: #ffffff;
}

.btn-secondary:hover {
    background-color: #4a4a4a;
}

/* Messages/Alerts */
.alert {
    padding: 15px 20px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.alert-success {
    background-color: rgba(46, 204, 113, 0.2);
    border-left: 4px solid #2ecc71;
    color: #2ecc71;
}

.alert-error {
    background-color: rgba(231, 76, 60, 0.2);
    border-left: 4px solid #e74c3c;
    color: #e74c3c;
}

/* Responsive */
@media (max-width: 768px) {
    .hero-title {
        font-size: 32px;
    }
    
    .posts-grid {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }
    
    .post-detail-title {
        font-size: 32px;
    }
}
```

---

## 📱 Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Netflix Blog{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/netflix.css' %}">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <a href="{% url 'blog:home' %}" class="navbar-brand">NETBLOG</a>
            
            <ul class="nav-links">
                <li><a href="{% url 'blog:home' %}">Home</a></li>
                {% if user.is_authenticated %}
                    <li><a href="{% url 'blog:post_create' %}">Create Post</a></li>
                    <li><a href="{% url 'accounts:profile' %}">Profile</a></li>
                    <li><a href="{% url 'accounts:logout' %}">Logout</a></li>
                {% else %}
                    <li><a href="{% url 'accounts:login' %}">Login</a></li>
                    <li><a href="{% url 'accounts:register' %}">Register</a></li>
                {% endif %}
            </ul>
        </div>
    </nav>

    <!-- Messages -->
    {% if messages %}
        <div style="padding: 100px 4% 20px; max-width: 1400px; margin: 0 auto;">
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">
                    {{ message }}
                </div>
            {% endfor %}
        </div>
    {% endif %}

    <!-- Main Content -->
    {% block content %}{% endblock %}

    <!-- Footer -->
    <footer style="text-align: center; padding: 40px; color: #808080; border-top: 1px solid #2a2a2a;">
        <p>&copy; 2024 Netflix Blog. All rights reserved.</p>
    </footer>
</body>
</html>
```

---

## 🏠 Home Template

```html
<!-- templates/blog/home.html -->
{% extends 'base.html' %}
{% load static %}

{% block content %}

<!-- Hero Banner -->
{% if featured_post %}
<div class="hero-banner" style="background-image: url('{{ featured_post.featured_image.url }}');">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <h1 class="hero-title">{{ featured_post.title }}</h1>
        <p class="hero-description">{{ featured_post.excerpt }}</p>
        <div class="hero-buttons">
            <a href="{% url 'blog:post_detail' featured_post.slug %}" class="btn-play">▶ Read Now</a>
            <a href="{% url 'blog:post_detail' featured_post.slug %}" class="btn-info">ℹ More Info</a>
        </div>
    </div>
</div>
{% endif %}

<!-- Posts Section -->
<div class="posts-section">
    <h2 class="section-title">Latest Posts</h2>
    
    <div class="posts-grid">
        {% for post in page_obj %}
        <div class="post-card">
            {% if post.featured_image %}
                <img src="{{ post.featured_image.url }}" alt="{{ post.title }}" class="post-card-image">
            {% else %}
                <div class="post-card-image" style="background-color: #3a3a3a;"></div>
            {% endif %}
            
            <div class="post-card-body">
                <a href="{% url 'blog:post_detail' post.slug %}" class="post-card-title">
                    {{ post.title }}
                </a>
                
                <div class="post-card-meta">
                    <span>{{ post.author.username }}</span>
                    <span>{{ post.created_at|date:"M d, Y" }}</span>
                </div>
                
                {% if post.category %}
                    <a href="#" class="category-badge">{{ post.category.name }}</a>
                {% endif %}
                
                <p class="post-card-excerpt">{{ post.excerpt|truncatewords:20 }}</p>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Pagination -->
    {% if page_obj.has_other_pages %}
    <div style="display: flex; justify-content: center; gap: 10px; margin-top: 40px;">
        {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}" class="btn btn-secondary">Previous</a>
        {% endif %}
        
        <span style="color: #808080; padding: 12px;">
            Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
        </span>
        
        {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}" class="btn btn-secondary">Next</a>
        {% endif %}
    </div>
    {% endif %}
</div>

{% endblock %}
```

---

## 📋 Grading Rubric (100 Points)

### Functionality (50 points)
- [ ] User registration works (10 pts)
- [ ] Login/logout works (10 pts)
- [ ] Create post works (10 pts)
- [ ] Edit post works (owner only) (5 pts)
- [ ] Delete post works (owner only) (5 pts)
- [ ] Comments work (5 pts)
- [ ] View count increments (5 pts)

### Netflix Design (25 points)
- [ ] Dark theme implemented (#141414 background) (5 pts)
- [ ] Hero banner with featured post (5 pts)
- [ ] Card grid layout (5 pts)
- [ ] Hover effects on cards (5 pts)
- [ ] Responsive design (5 pts)

### Code Quality (15 points)
- [ ] Models properly structured (5 pts)
- [ ] Views follow best practices (5 pts)
- [ ] Templates use inheritance (5 pts)

### Polish (10 points)
- [ ] No console errors (3 pts)
- [ ] Forms have validation (3 pts)
- [ ] Good user experience (4 pts)

---

## ⚙️ Setup Instructions

### 1. Create Project
```bash
django-admin startproject netflix_blog
cd netflix_blog
python manage.py startapp accounts
python manage.py startapp blog
```

### 2. Install Dependencies
```bash
pip install Pillow
```

### 3. Configure Settings
Add to `settings.py`:
```python
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'blog:home'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Server
```bash
python manage.py runserver
```

---

## 🎯 Tips for Success

### Don't Copy Each Other
Even though everyone builds the same project, instructors will check for:
- Variable naming
- Code organization
- Comment styles
- Small implementation differences

### Focus On
1. **Clean code** - proper indentation, naming
2. **Working features** - test everything
3. **Netflix aesthetics** - dark theme, smooth transitions
4. **Unique touches** - small UI improvements

### Use Claude AI Sessions For
- "How do I make the hero banner image darker?"
- "Help me fix this error: [paste error]"
- "How do I make cards scale on hover?"
- "Show me how to add view counter"

---

## 📦 Deliverables

1. **GitHub Repository**
2. **README.md** with setup instructions
3. **Screenshots** (at least 5):
   - Homepage with hero
   - Post grid
   - Post detail
   - Create post form
   - User profile
4. **Demo Video** (3-5 mins)

---

Good luck! 🍿🎬
