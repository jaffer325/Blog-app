from django.shortcuts import redirect
from django.urls import reverse

class RedirectAuthenicatedUserMiddleware:
   def __init__(self,get_response):
      self.get_response = get_response

   def __call__(self,request):
      
      #Checks the user is authenticated
      if request.user.is_authenticated:
         #List of paths to check
         paths_to_redirect = [reverse("polls:register"),reverse("polls:login")]

         if request.path in paths_to_redirect:
            return redirect("polls:index")
         
      
      response = self.get_response(request)
      return response


class RestrictUnAuthenicatedUserMiddleware:
   def __init__(self,get_response):
      self.get_response = get_response

   def __call__(self,request):
      #Checks the user is unauthenticated
      restricted_paths = [reverse("polls:dashboard"),reverse("polls:logout")]
      if not request.user.is_authenticated and request.path in restricted_paths:
         return redirect("polls:login")
         
      response = self.get_response(request)
      return response