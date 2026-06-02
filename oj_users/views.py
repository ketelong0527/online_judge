from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from django.core.paginator import Paginator


def user_list(request):
    users = User.objects.filter(is_active=True).order_by('-rating')
    
    for user in users:
        user.update_stats()
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'oj_users/user_list.html', {
        'page_obj': page_obj
    })


def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    user.update_stats()
    solved_problems = user.submissions.filter(status='Accepted').values('problem').distinct()
    
    return render(request, 'oj_users/user_detail.html', {
        'user': user,
        'solved_count': solved_problems.count()
    })


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
            return render(request, 'oj_users/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已被注册')
            return render(request, 'oj_users/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'oj_users/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        messages.success(request, '注册成功！请登录')
        return redirect('/users/login/')
    
    return render(request, 'oj_users/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功！')
            next_url = request.GET.get('next', '/problems/')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
            return render(request, 'oj_users/login.html')
    
    return render(request, 'oj_users/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, '已成功退出登录')
    return redirect('/problems/')


@login_required
def profile(request):
    user = request.user
    user.update_stats()
    solved_problems = user.submissions.filter(status='Accepted').values('problem').distinct()
    
    return render(request, 'oj_users/profile.html', {
        'user': user,
        'solved_count': solved_problems.count()
    })


class UserAPI(View):
    def get(self, request):
        users = User.objects.filter(is_active=True).order_by('-rating').values(
            'id', 'username', 'rating', 'rank', 'total_solved', 'acceptance_rate'
        )[:50]
        return JsonResponse({'users': list(users)})


class UserDetailAPI(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username, is_active=True)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'rating': user.rating,
            'rank': user.rank,
            'total_solved': user.total_solved,
            'total_submissions': user.total_submissions,
            'accepted_submissions': user.accepted_submissions,
            'acceptance_rate': user.acceptance_rate,
            'github_url': user.github_url,
            'blog_url': user.blog_url,
            'school': user.school,
            'location': user.location,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return JsonResponse(data)
