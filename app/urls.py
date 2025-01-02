from django.urls import path 
from .views import HomePageView, AboutPageView, CaloriePageView, AccountPageView, SignInPageView, SignUpPageView, EditAccountView, DeleteAccountView, logout_view

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'), 
    path('about/', AboutPageView.as_view(), name='about'), 
    path('calorie/', CaloriePageView.as_view(), name='calorie'),
    path('account/', AccountPageView.as_view(), name='account'),
    path('', SignInPageView.as_view(), name='login'),
    path('sign-up/', SignUpPageView.as_view(), name='signup'),
    path('account/edit/<int:pk>/', EditAccountView.as_view(), name='edit_account'),
    path('account/delete/<int:pk>//', DeleteAccountView.as_view(), name='delete_account'),
    path('logout/', logout_view, name='logout'),
]
