import json
from django.db import IntegrityError
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView
from django.views import View
from .forms import UserProfileForm
from django.contrib.auth.models import User
from .models import Exercise, ExerciseProgram, FoodPresetCalorie, Membership, UserProfile
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator 
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.mixins import UserPassesTestMixin

class HomePageView(TemplateView):
    template_name = 'app/home.html'

@csrf_exempt
def update_membership(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            membership_type = data.get("membership_type")

            # Ensure user_id is retrieved from session
            user_id = request.session.get("user_id")
            if not user_id:
                return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

            # Fetch user profile
            user = UserProfile.objects.get(user_id=user_id)

            # Ensure membership exists, or create one
            membership, created = Membership.objects.get_or_create(user_membership=user)

            # Update membership type
            membership.type = membership_type
            membership.save()

            return JsonResponse({"status": "success", "message": f"Membership updated to {membership_type}"})

        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "User or membership not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

class AboutPageView(TemplateView):
    template_name = 'app/about.html'

class CaloriePageView(TemplateView):
    template_name = 'app/calorie.html'

    def dispatch(self, request, *args, **kwargs):
        # ✅ Allow Django admins (staff users) to access
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return super().dispatch(request, *args, **kwargs)

        # Ensure a regular user is logged in
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('login')

        # Check the user's membership type
        try:
            user = UserProfile.objects.get(user_id=user_id)
            membership = Membership.objects.get(user_membership=user)

            # Restrict access for Basic users
            if membership.type not in ['Premium', 'VIP']:
                messages.warning(request, "This page is only accessible to Premium and VIP members. Upgrade your membership to gain access.")
                return redirect('home')  # Redirect to home with a warning
        except (UserProfile.DoesNotExist, Membership.DoesNotExist):
            messages.error(request, "Your membership could not be verified. Please contact support.")
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['food_presets'] = FoodPresetCalorie.objects.all()
        return context
    
@csrf_exempt
def add_food_preset(request):
    if request.method == "POST":
        food_name = request.POST.get("food_name")
        calories = request.POST.get("calories")
        food_pic = request.FILES.get("food_pic")

        FoodPresetCalorie.objects.create(
            food_name=food_name, calories=calories, food_pic=food_pic
        )
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"}, status=400)

def get_food_presets(request):
    food_presets = FoodPresetCalorie.objects.all()
    data = [
        {
            "food_id": food.food_id,
            "food_name": food.food_name,
            "calories": food.calories,
            "food_pic": food.food_pic.url if food.food_pic else "",
        }
        for food in food_presets
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def delete_food_preset(request, food_id):
    if request.method == "DELETE":
        try:
            preset = FoodPresetCalorie.objects.get(food_id=food_id)
            preset.delete()
            return JsonResponse({"status": "success"})
        except FoodPresetCalorie.DoesNotExist:
            return JsonResponse({"status": "not_found"}, status=404)

    return JsonResponse({"status": "failed"}, status=400)

class ProgramPageView(ListView):
    model = ExerciseProgram
    context_object_name = 'exercise_programs'
    template_name = 'app/program.html'

@csrf_exempt
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get('category_name').strip()
        category_pic = request.FILES.get('category_pic')  

        if category_name:
            try:
                ExerciseProgram.objects.create(category=category_name, category_pic=category_pic)
                return redirect('programs')  
            except IntegrityError:
                return render(request, 'app/program.html', {
                    'exercise_programs': ExerciseProgram.objects.all(),
                    'error_message': f"The category '{category_name}' already exists.",
                })
    return render(request, 'app/program.html', {
        'exercise_programs': ExerciseProgram.objects.all(),
        'error_message': "Invalid request. Please provide a category name.",
    })  

@csrf_exempt
def delete_category(request):
    if request.method == "POST":
        category_id = request.POST.get('category')
        try:
            category = ExerciseProgram.objects.get(exercise_program_id=category_id)
            category.delete()
            return redirect('programs')  
        except ExerciseProgram.DoesNotExist:
            return HttpResponse("Category not found", status=404)
    return HttpResponse("Invalid request", status=405)

class ExercisePageView(DetailView):
    model = ExerciseProgram
    context_object_name = 'exercise_program'
    template_name = 'app/exercise.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercises'] = Exercise.objects.filter(exercise_program=self.object)
        return context
    
@csrf_exempt
def add_exercise(request):
    if request.method == "POST":
        exercise_name = request.POST.get("exercise_name")
        description = request.POST.get("description", "")
        calories_burned = request.POST.get("calories_burned")
        duration_minutes = request.POST.get("duration_minutes")
        exercise_program_id = request.POST.get("exercise_program_id")

        exercise_program = get_object_or_404(ExerciseProgram, pk=exercise_program_id)

        Exercise.objects.create(
            name=exercise_name,
            description=description,
            calories_burned=calories_burned,
            duration_minutes=duration_minutes,
            exercise_program=exercise_program
        )
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "failed"}, status=400)

@csrf_exempt
def delete_exercise(request, exercise_id):
    if request.method == "DELETE":
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            exercise.delete()
            return JsonResponse({"status": "success"})
        except Exercise.DoesNotExist:
            return JsonResponse({"status": "not_found"}, status=404)

    return JsonResponse({"status": "failed"}, status=400)

class SessionLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_id'):
            messages.error(request, "You must be logged in to access this page.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class AccountPageView(ListView):
    model = UserProfile
    template_name = 'app/account.html'
    context_object_name = 'account_details'

    def get_queryset(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            return UserProfile.objects.filter(user_id=user_id).prefetch_related(
                Prefetch('membership_set')
            )
        return UserProfile.objects.none()

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
        user = form.save() 
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

class EditAccountView(SessionLoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'app/edit_account.html'

    def get_object(self, queryset=None):
        user_id = self.request.session.get('user_id')
        if user_id:
            try:
                return UserProfile.objects.get(user_id=user_id)
            except UserProfile.DoesNotExist:
                raise Http404("User profile not found.")
        else:
            raise Http404("No user ID found in session. Please log in again.")

    def get_success_url(self):
        return reverse_lazy('account')
    
class DeleteAccountView(SessionLoginRequiredMixin, DeleteView):
    model = UserProfile  # Use UserProfile model instead of User
    template_name = 'app/delete_account.html'
    success_url = reverse_lazy('login')

    def get_object(self, queryset=None):
        user_id = self.request.session.get('user_id')
        if user_id:
            try:
                return UserProfile.objects.get(user_id=user_id)
            except UserProfile.DoesNotExist:
                raise Http404("User profile not found.")
        else:
            raise Http404("No user ID found in session. Please log in again.")

    def post(self, request, *args, **kwargs):
        """Override POST method to handle deletion and redirect."""
        # Get the object and delete it
        self.object = self.get_object()
        self.object.delete()

        # Clear session and log out
        logout(request)
        request.session.flush()

        # Add a success message
        messages.success(request, "Your account has been deleted.")
        
        # Redirect to success URL
        return HttpResponseRedirect(self.success_url)

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# Admin Signup View
@method_decorator(csrf_exempt, name='dispatch')
def admin_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "app/admin_signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "app/admin_signup.html")

        # Create a new admin user
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True  # Set as staff to allow admin access
        user.save()

        messages.success(request, "Admin account created successfully. Please log in.")
        return redirect("admin_login")

    return render(request, "app/admin_signup.html")


# Admin Login View
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Authenticate admin user
        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! You are logged in as an admin.")
            return render(request, "app/account.html")
        else:
            messages.error(request, "Invalid username or password, or you do not have admin access.")
            return render(request, "app/admin_login.html")

    return render(request, "app/admin_login.html")