from django.contrib import admin
from .models import Membership, ExerciseProgram, Exercise, CalorieIntake, Attendance, UserProfile, FoodPresetCalorie

admin.site.register(UserProfile)
admin.site.register(Membership)
admin.site.register(ExerciseProgram)
admin.site.register(Exercise)
admin.site.register(CalorieIntake)
admin.site.register(Attendance)
admin.site.register(FoodPresetCalorie)

