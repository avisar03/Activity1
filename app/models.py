from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from django.utils.timezone import now

class ExerciseProgram(models.Model):
    exercise_program_id = models.BigAutoField(primary_key=True, unique=True)
    category_pic = models.ImageField(null=True, blank=True,upload_to="media/category/")
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category

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
    food_pic = models.ImageField(null=True, blank=True,upload_to="media/category/")
    food_name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()  

    def __str__(self):
        return f"{self.food_name}, Calorie: {self.calories}"

class Exercise(models.Model):
    exercise_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    calories_burned = models.PositiveIntegerField()  # Estimated calories burned per session
    duration_minutes = models.PositiveIntegerField()  # Duration of exercise in minutes
    exercise_program = models.ForeignKey(ExerciseProgram, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} in {self.exercise_program.category}"
 
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

