# Generated by Django 5.1.1 on 2024-12-16 19:00

import app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseProgram',
            fields=[
                ('exercise_program_id', models.BigAutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('duration_weeks', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='FoodPresetCalorie',
            fields=[
                ('food_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('food_name', models.CharField(max_length=100)),
                ('calories', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('birth_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('exercise_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('calories_burned', models.PositiveIntegerField()),
                ('duration_minutes', models.PositiveIntegerField()),
                ('exercise_program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.exerciseprogram')),
                ('user_exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='CalorieIntake',
            fields=[
                ('calorie_intake_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(auto_now_add=True)),
                ('calories', models.PositiveIntegerField(blank=True, null=True)),
                ('food_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.foodpresetcalorie')),
                ('user_calorie_intake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attedance_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('time_in', models.TimeField()),
                ('time_out', models.TimeField(blank=True, null=True)),
                ('user_attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('membership_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('Basic', 'Basic'), ('Premium', 'Premium'), ('VIP', 'VIP')], default='Basic', max_length=10)),
                ('start_date', models.DateField(auto_now_add=True)),
                ('end_date', models.DateField(default=app.models.default_end_date)),
                ('user_membership', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userprofile')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user_membership', 'type'), name='unique_user_membership')],
            },
        ),
    ]
