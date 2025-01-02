from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

class ExerciseProgram(models.Model):
    exercise_program_id = models.BigAutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duration_weeks = models.PositiveIntegerField()  # Length of program in weeks

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)  
    last_name = models.CharField(max_length=100)   
    email = models.EmailField(unique=True)         
    address = models.CharField(max_length=255, blank=True)  
    phone_number = models.CharField(max_length=15, blank=True)  
    birth_date = models.DateField(null=True, blank=True) 
    password = models.CharField(max_length=255) 

    def __str__(self):
        return f"Profile of {self.first_name}"
    
class FoodPresetCalorie(models.Model):
    food_id = models.BigAutoField(primary_key=True)
    food_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()  # Calories for this specific food

    def __str__(self):
        return f"{self.food_name}, Calorie: {self.calories}"

class Exercise(models.Model):
    exercise_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    calories_burned = models.PositiveIntegerField()  # Estimated calories burned per session
    duration_minutes = models.PositiveIntegerField()  # Duration of exercise in minutes
    exercise_program = models.ForeignKey(ExerciseProgram, on_delete=models.CASCADE)
    user_exercise = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} in {self.exercise_program.name}"

class CalorieIntake(models.Model):
    calorie_intake_id = models.BigAutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    calories = models.PositiveIntegerField(null=True, blank=True)  # Calories for this specific intake if food are not in the FoodPreset
    food_item = models.ForeignKey(FoodPresetCalorie, null=True, blank=True, on_delete=models.CASCADE)
    user_calorie_intake = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        # Check if there's a food item associated with this intake
        if self.food_item:
            return f"{self.food_item.food_name} ({self.food_item.calories} kcal) intake by {self.user_calorie_intake.first_name} on {self.date}"
        else:
            # Default message if no food item is associated
            return f"{self.calories} kcal intake by {self.user_calorie_intake.first_name} on {self.date}"
    
class Attendance(models.Model):
    attedance_id = models.BigAutoField(primary_key=True)
    date = models.DateField()
    time_in = models.TimeField()
    time_out = models.TimeField(blank=True, null=True)
    user_attendance = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attendance for {self.user_attendance.first_name} on {self.date}"
    
def default_end_date():
    return now().date() + timedelta(days=365)

class Membership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('Basic', 'Basic'),
        ('Premium', 'Premium'),
        ('VIP', 'VIP'),
    ]
    membership_id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, default='Basic')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(default=default_end_date)  # Use callable here
    user_membership = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_membership', 'type'], name='unique_user_membership')
        ]

    def __str__(self):
        return f"{self.user_membership.first_name}'s {self.type} Membership"
    
@receiver(post_save, sender=UserProfile)
def create_default_membership(sender, instance, created, **kwargs):
    if created:  # Only when a new UserProfile is created
        Membership.objects.create(user_membership=instance, type='Basic')

