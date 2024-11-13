from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, zip_code, city, password=None, role = "user"):
        user = self.model(email = email, first_name = first_name, last_name = last_name, zip_code = zip_code, city = city, role = role)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, email, first_name, last_name, zip_code, city, password=None, role = "admin"):
        user = self.create_user(email = email, first_name = first_name, last_name = last_name, zip_code = zip_code, city = city, role = role)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    role = models.CharField(max_length=20, default="user")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'zip_code', 'city']

    def __str__(self):
        return self.email
