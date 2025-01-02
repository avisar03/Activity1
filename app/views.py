from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView
from django.views import View
from .forms import UserProfileForm
from .models import UserProfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate
from django.contrib.auth.hashers import check_password
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

class HomePageView(TemplateView):
    template_name = 'app/home.html'

class AboutPageView(TemplateView):
    template_name = 'app/about.html'

class CaloriePageView(TemplateView): 
    template_name = 'app/calorie.html'

class AccountPageView(ListView):
    model = UserProfile
    template_name = 'app/account.html'
    context_object_name = 'account_details'

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return UserProfile.objects.filter(user_id=user_id)
        else:
            return UserProfile.objects.none()  # Return an empty queryset if not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.get('user_first_name'):
            context['user_first_name'] = self.request.session['user_first_name']
        else:
            context['user_first_name'] = 'Account'
        return context

class SignUpPageView(CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'app/sign_up.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()  # No need to hash the password here
        messages.success(self.request, "Account created successfully! Please log in.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error in the form. Please try again.")
        return self.render_to_response({'form': form})

class SignInPageView(View):
    def get(self, request):
        return render(request, 'app/sign_in.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user using the custom backend
        user = authenticate(request, username=email, password=password, backend='app.authentication_backends.EmailBackend')

        if user:
            # If user is authenticated, manually set the user in the session
            request.session['user_first_name'] = user.first_name
            request.session['user_id'] = user.user_id
            request.session['user_email'] = user.email
            # Optionally, set request.user manually (but this is not strictly necessary)
            request.user = user
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect('home')
        else:
            # If authentication fails, show an error message
            messages.error(request, "Invalid email or password.")
            return render(request, 'app/sign_in.html')

class EditAccountView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'app/edit_account.html'

    def get_object(self, queryset=None):
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            raise Http404("User profile not found.")

    def get_success_url(self):
        return reverse_lazy('account')
    
class DeleteAccountView(LoginRequiredMixin, DeleteView):
    model = UserProfile  # Use UserProfile model instead of User
    template_name = 'app/delete_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')  # Use 'user_id' from the URL
        try:
            return UserProfile.objects.get(user_id=user_id)  # Get the correct user profile
        except UserProfile.DoesNotExist:
            raise Http404("User not found.")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        logout(request)  # Clear the session and log out the user
        request.session.flush()
        messages.success(request, "Your account has been deleted.")
        return response

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')
