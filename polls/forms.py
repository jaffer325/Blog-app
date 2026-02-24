from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from polls.models import Category, Post
class ContactForm(forms.Form):
    name = forms.CharField(label='Name',max_length=100,required=True)
    email = forms.EmailField(label='Email',required=True)
    message = forms.CharField(label='Message', required=True)


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Username',max_length=100,required=True)
    email = forms.EmailField(label='Email',max_length=100,required=True)
    password = forms.CharField(label='Password',max_length=100, required=True)
    password_confirm = forms.CharField(label='Confirm Password',max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username','email','password']
    
    #custom validation
    def clean(self):
        cleaned_data =  super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")



class LoginForm(forms.Form):
    username = forms.CharField(label="Username",max_length=100,required=True)
    password = forms.CharField(label="Password",max_length=100,required=True)
    
    #custom validation
    def clean(self):
       cleaned_data = super().clean()

       username = cleaned_data.get('username')
       password = cleaned_data.get('password')

       if username and password:
           user = authenticate(username=username,password=password)
           if user is None:
               raise forms.ValidationError("USER NOT EXISTS")


class ForgotPasswordForm(forms.Form):
    email = forms.CharField(label="Email",required=True,max_length=100)
     
    #custom validation
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No User Registrated with this email")



class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(label="New Password",min_length=8,required=True)
    confirm_password = forms.CharField(label="Confirm Password",min_length=8,required=True)


    #Custom Validation
    def clean(self):
      cleaned_data =  super().clean()
      new_password = cleaned_data.get('new_password')
      confirm_password = cleaned_data.get('confirm_password')

      if new_password and confirm_password and new_password != confirm_password:
         raise forms.ValidationError("Passwords do not match.")


class PostForm(forms.ModelForm):
    title = forms.CharField(label="Title",min_length=5,max_length=100,required=True,)
    content = forms.CharField(label="Content",min_length=10,required=True,)
    Category = forms.ModelChoiceField(label="Category",required=True,queryset=Category.objects.all())
    img_url = forms.ImageField(label="Image",required=False)

    class Meta:
        model = Post
        fields = ["title","content","Category",'img_url']

    
    def save(self, commit = ...):
        post = super().save(commit)
        
        cleaned_data = super().clean()

        if cleaned_data.get('img_url'):
            post.img_url = cleaned_data.get('img_url')
        else:
            post.img_url = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
       
        if commit:
            post.save()

        return post
