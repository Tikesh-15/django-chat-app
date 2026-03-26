from django.db import models
from django.contrib.auth.models import User

# 1. Profile Model: User ki extra details (DP, Block list) ke liye
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='default.png')
    # Many-to-Many logic for blocking
    blocked_users = models.ManyToManyField(User, related_name='blocked_by', blank=True)

    def __str__(self):
        return self.user.username

# 2. Message Model: Chats aur Files save karne ke liye
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True) 
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Message Read/Unread status
    is_read = models.BooleanField(default=False) 
    
    # "Delete for me" logic: Agar koi user chat clear karta hai
    deleted_by = models.ManyToManyField(User, related_name='deleted_messages', blank=True)

    class Meta:
        ordering = ['timestamp'] # Messages hamesha chronological order mein rahenge

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.timestamp.strftime('%H:%M')})"

# 3. Contact Model: Nickname/Alias save karne ke liye
class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_contacts')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_entries')
    nickname = models.CharField(max_length=100)

    class Meta:
        unique_together = ('user', 'friend') # Same user-friend pair duplicate nahi hoga

    def __str__(self):
        return f"{self.user.username} saved {self.friend.username} as {self.nickname}"
    

class StrangerQueue(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room_id = models.CharField(max_length=100, null=True, blank=True)
    is_matched = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username