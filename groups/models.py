from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import misaka
from django.urls import reverse

User = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField(max_length=300, blank=True, default='')
    description_html = models.TextField(editable=False, default='', blank=True)
    members = models.ManyToManyField(User, through="GroupMember")  # fixed typo
    
    class Meta:
        ordering = ['name']
        
    def save(self, *args, **kwargs):
        self.description_html = misaka.html(self.description)  # Always update
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("groups:single", kwargs={"slug": self.slug})
    
    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, related_name='memberships', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_groups", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
    
    class Meta:
        unique_together = ('group', 'user')
