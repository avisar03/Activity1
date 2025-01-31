from django.conf import settings
from django.conf.urls.static import static
from django.urls import path 
from .views import ExercisePageView, HomePageView, AboutPageView, CaloriePageView, ProgramPageView, AccountPageView, SignInPageView, SignUpPageView, EditAccountView, DeleteAccountView, add_category, add_exercise, add_food_preset, admin_login, admin_signup, delete_category, delete_exercise, delete_food_preset, get_food_presets, logout_view, update_membership

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'), 
    path('about/', AboutPageView.as_view(), name='about'), 
    path('calorie/', CaloriePageView.as_view(), name='calorie'),
    path('account/', AccountPageView.as_view(), name='account'),
    path('', SignInPageView.as_view(), name='login'),
    path('sign-up/', SignUpPageView.as_view(), name='signup'),
    path('account/edit/', EditAccountView.as_view(), name='edit_account'),
    path('account/delete/', DeleteAccountView.as_view(), name='delete_account'),
    path('logout/', logout_view, name='logout'),
    path('programs/', ProgramPageView.as_view(), name='programs'),
    path('add-category/', add_category, name='add_category'),
    path('delete-category/', delete_category, name='delete_category'),
    path('exercise/<int:pk>/', ExercisePageView.as_view(), 
    name='exercise_program_detail'),
    path('add-food-preset/', add_food_preset, name='add_food_preset'),
    path('get-food-presets/', get_food_presets, name='get_food_presets'),
    path('delete-food-preset/<int:food_id>/', delete_food_preset, name='delete_food_preset'),
    path("admin-signup/", admin_signup, name="admin_signup"),
    path("admin-login/", admin_login, name="admin_login"),
    path("update-membership/", update_membership, name="update_membership"),
    path('add-exercise/', add_exercise, name='add_exercise'),
    path('delete-exercise/<int:exercise_id>/', delete_exercise, name='delete_exercise'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)