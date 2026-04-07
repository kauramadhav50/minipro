from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Built-in fields already included: username, email, password, is_staff, is_active
    
    # Custom LinkedIn-style fields
    fullname = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True, null=True)

    # Use email as a required field for LinkedIn-style login (optional)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

# Now update your Post model to point to this new User
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}"