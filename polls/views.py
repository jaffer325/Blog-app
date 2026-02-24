
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse,Http404
from django.urls import reverse
import logging
from .models import Category, Post,AboutUs
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPasswordForm,LoginForm, PostForm,RegisterForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,permission_required
# Create your views here.

app_name = 'blog'

# static data 
# posts = [
#         {"id" : 1,"title" : "Post 1","content" : "Content of Post 1"},
#         {"id" : 2,"title" : "Post 2","content" : "Content of Post 2"},
#         {"id" : 3,"title" : "Post 3","content" : "Content of Post 3"},
#         {"id" : 4,"title" : "Post 4","content" : "Content of Post 4"},
#         {"id" : 5,"title" : "Post 5","content" : "Content of Post 5"}
# ]


def index(request):
    blog_title = "Current Post"
    app_name = "Personal Blog"

    all_posts = Post.objects.filter(is_published=True)
    paginator = Paginator(all_posts,6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request,"index.html",{"blog_title" : blog_title ,"app_name" : app_name,"page_obj" : page_obj})


def detail(request,slug):
    if request.user and not request.user.has_perm("polls.view_post"):
        messages.error(request,"You have no permission to view any post")
        return redirect('polls:index')


    # #getting static id
    # post = next((item for item in posts if item['id'] == int(post_id)),None)
    try:
        post = Post.objects.get(slug=slug)
        related_posts = Post.objects.filter(Category = post.Category).exclude(pk=post.id)
    
    except Post.DoesNotExist:
        raise Http404("Post Does not Exist!")
    # log = logging.getLogger()
    # log.debug(f"post variable is {post}")

    return render(request,"detail.html",{"post" : post,"related_posts" : related_posts})

# //redirect
def old_url_redirect(request):
    return redirect(reverse("polls:new_url"))

def new_url(request):
    username = "esakki"
    return HttpResponse(f"New {username} url page")

def contact(request):
   if request.method == 'POST':
       form = ContactForm(request.POST)
       name = request.POST.get('name')
       email = request.POST.get('email')
       message = request.POST.get('message')

       log = logging.getLogger(__name__)
       if form.is_valid():
        #print the data
        # log.debug(f"Post data is {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}")
          success_message = "Message Sent Successfully"
          return render(request,'contact.html',{"form":form,"success_message":success_message})
       else:
           log.debug('Form Validtion Failure')
       return render(request,'contact.html',{"form":form,"name":name,"email":email,"message":message})
   return render(request,'contact.html')

def about(request):
    about_content = AboutUs.objects.first()
    if about_content is None or not about_content.content:
        about_content = "Default content goes here." #Default text
    else:
        about_content = about_content.content

    return render(request,'about.html',{"about_content":about_content})


def register(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            #add user to readers group
            reader_group,_ = Group.objects.get_or_create(name="Readers")
            user.groups.add(reader_group)

            messages.success(request,"Registration Sucessfully!")
            return redirect("polls:login")

    
    return render(request,'register.html',{"form":form})


def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
          username = form.cleaned_data['username']
          password = form.cleaned_data['password']         
          user = authenticate(username=username,password=password)
          if user is not None:
              auth_login(request,user)
              
              return redirect("polls:dashboard")

    return render(request,'login.html',{"form":form})


def dashboard(request):
    blog_title = "My Posts"
    #getting user post
    all_posts = Post.objects.filter(user=request.user)
    paginator = Paginator(all_posts,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"dashboard.html",{"blog_title":blog_title,"page_obj":page_obj})


def logout(request):
    auth_logout(request)
    return redirect("polls:index")

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            print(user)
            #send email to reset password
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain

            subject = "Reset Password requested"
            message = render_to_string('reset_password_email.html',{"domain":domain,"token":token,"uid":uid})
            
            send_mail(subject,message,"noreply@jvlcode.com",[email])
            messages.success(request,"Email has been send")
            return redirect("polls:forgot_password") 

    return render(request,'forgot_password.html',{"form":form})


def reset_password(request,uidb64,token):
    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
          new_password = form.cleaned_data['new_password']
          try:
             uid = urlsafe_base64_decode(uidb64)
             user = User.objects.get(pk=uid)
          except(TypeError,ValueError,OverflowError,User.DoesNotExist):
             user = None

          if user is not None and default_token_generator.check_token(user,token):
              user.set_password(new_password)
              user.save()
              messages.success(request,"Your password has reset successfully!")
              return redirect('polls:login')
          else:
              messages.error(request,"Password reset link is invalid")

    

 
    return render(request,'reset_password.html',{"form":form})
    
@login_required
@permission_required('polls.add_post',raise_exception=True)
def new_post(request):
  form = PostForm()
  categories = Category.objects.all()
  if request.method == 'POST':
      form = PostForm(request.POST,request.FILES)
      if form.is_valid():
          post = form.save(commit=False)
          post.user = request.user
          post.save()
          return redirect('polls:dashboard')
      
  return render(request,'new_post.html',{"categories": categories,"form":form})


@login_required
@permission_required('polls.change_post',raise_exception=True)
def edit_post(request,post_id):
   post = get_object_or_404(Post, id=post_id)

    # Check ownership
   if post.user != request.user:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect('polls:dashboard')
   form = PostForm()
   categories = Category.objects.all()
   post = get_object_or_404(Post,id = post_id)
   if request.method == 'POST':
       form = PostForm(request.POST,request.FILES,instance=post)
       if form.is_valid():
           form.save()
           messages.success(request,"Your post has been edited successfully!")
           return redirect('polls:dashboard')

   return render(request,'edit_post.html',{"categories": categories,"post":post,"form":form})
    
@login_required
@permission_required('polls.delete_post',raise_exception=True)
def delete_post(request,post_id):
     post = get_object_or_404(Post,id = post_id)
     post.delete()
     messages.success(request,"Post Deleted Successfully!")
     return redirect('polls:dashboard')

@login_required
def publish_post(request,post_id):
    post = get_object_or_404(Post,id = post_id)
    post.is_published = True
    post.save()
    messages.success(request,"Post Published Successfully!")
    return redirect('polls:dashboard')
