from django.shortcuts import redirect
from .models import seller,User

def logout_required(view_func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        
        return view_func(request,*args,**kwargs)
    return wrapper

def seller_required(view_func):
    def wrapper(request,*args,**kwargs):

        if not request.user.is_authenticated:
            return redirect('seller_login')


        if not seller.objects.filter(user=request.user).exists():
            return redirect('home')
        
        return  view_func(request,*args,**kwargs)
    return wrapper

def seller_logout_required(view_func):
    def wrapper(request,*args,**kwargs):

        if request.user.is_authenticated:
            if seller.objects.filter(user=request.user).exists():
                return redirect('seller_index')
            return redirect('home')
        return view_func(request,*args,**kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request,*args,**kwargs):

        if not request.user.is_authenticated:
            return redirect('admin_login')


        if not request.user.is_staff:
            return redirect('home')
        
        return  view_func(request,*args,**kwargs)
    return wrapper

def admin_logout_required(view_func):
    def wrapper(request,*args,**kwargs):

        if request.user.is_authenticated:
            if User.objects.filter(user=request.user).exists():
                return redirect('admin_index')
            return redirect('home')
        return view_func(request,*args,**kwargs)
    return wrapper