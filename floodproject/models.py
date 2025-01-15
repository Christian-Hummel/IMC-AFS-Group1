from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, latitude, longitude, password=None, role = "user"):
        user = self.model(email = email, first_name = first_name, last_name = last_name, latitude=latitude, longitude=longitude,role = role)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, first_name, last_name, latitude=47.7972, longitude=13.0477, password=None, role = "admin"):
        user = self.create_user(email = email, first_name = first_name, last_name = last_name, latitude=latitude, longitude=longitude, role = role)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        AGENT = 'agent', 'Agent'
        MANAGER = 'manager', 'Manager'
        ADMIN = 'admin', 'Admin'
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    latitude = models.FloatField(max_length=10, default=47.4231277, null=False, blank=False)
    longitude = models.FloatField(max_length=10, default=13.6539813, null=False, blank=False)
    role = models.CharField(max_length=20, choices=Role.choices,default=Role.USER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    code = models.CharField(max_length=6, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def create_code(self):
        self.code = random.randint(100000,999999)

    def __str__(self):
        return self.email


class Report(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    lon = models.FloatField()
    lat = models.FloatField()
    picture_description = models.CharField(max_length=100,default="",blank=True,null=True)
    picture = models.ImageField(upload_to='images/',default=0)
    user = models.ForeignKey(CustomUser,null=False, on_delete=models.CASCADE,related_name='reports')
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.description} - {self.lat} - {self.lon} - {self.user_id}"

class Task(models.Model):
    class Status(models.TextChoices):
        TO_DO = 'To-Do', 'To-Do'
        IN_PROGRESS = 'In Progress', 'In Progress'
        DONE = 'Done', 'Done'
    description = models.CharField(max_length=100)
    manager = models.ForeignKey(CustomUser, related_name='managed_tasks', on_delete=models.CASCADE)
    agent = models.ManyToManyField(CustomUser,related_name='agents_tasks')
    report = models.ForeignKey(Report,on_delete=models.CASCADE)
    assigned_date = models.CharField(max_length=100)
    due_date = models.CharField(max_length=100)
    latitude = models.FloatField(max_length=10, default=47.4231277, null=False, blank=False)
    longitude = models.FloatField(max_length=10, default=13.6539813, null=False, blank=False)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.TO_DO)

    def __str__(self):
        return f"{self.description} - {self.manager} - {self.agent} - {self.assigned_date} - {self.due_date} - {self.status}"

class Vote(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    validity = models.BooleanField(default=True)
    rating = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ]
    )

    class Meta:
        unique_together = ('report','user')

    def __str__(self):
        return f"{self.report_id} - {self.user_id} - {self.rating} - {self.validity}"


class Comment(models.Model):
    comment = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    username = models.CharField(max_length=256, default="")
    date = models.DateTimeField(auto_now=True)


class Subscription(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


    class Meta:
        unique_together = ('report','user')

    def __str__(self):
        return f"{self.report_id} - {self.user_id} - {self.active}"


class Notification(models.Model):
    title = models.CharField(max_length=256, default="")
    description = models.TextField(default="")
    time = models.DateTimeField(auto_now=True)
    read = models.BooleanField(default=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


    def __str__(self):
        return f"{self.title} - {self.description} - {self.time} - {self.read}"