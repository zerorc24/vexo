from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ==========================================
# PROFILE
# ==========================================
class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    bio = models.CharField(
        max_length=120,
        blank=True
    )

    online = models.BooleanField(
        default=False
    )

    typing = models.BooleanField(
        default=False
    )

    last_seen = models.DateTimeField(
        default=timezone.now
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username


# ==========================================
# ROOM
# ==========================================
class Room(models.Model):

    ROOM_TYPES = (
        ("private", "Private"),
        ("group", "Group"),
    )

    name = models.CharField(
        max_length=255,
        unique=True
    )

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES,
        default="private"
    )

    participants = models.ManyToManyField(
        User,
        related_name="chat_rooms"
    )

    group_avatar = models.ImageField(
        upload_to="group_avatars/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    # LAST MESSAGE
    def last_message(self):

        return self.messages.last()


# ==========================================
# MESSAGE
# ==========================================
class Message(models.Model):

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    content = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="chat_images/",
        blank=True,
        null=True
    )

    voice = models.FileField(
        upload_to="voice_notes/",
        blank=True,
        null=True
    )

    is_read = models.BooleanField(
        default=False
    )

    edited = models.BooleanField(
        default=False
    )

    deleted = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):

        if self.content:
            return f"{self.sender.username}: {self.content[:30]}"

        return f"{self.sender.username}: Media Message"


# ==========================================
# MESSAGE REACTION
# ==========================================
class Reaction(models.Model):

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    emoji = models.CharField(
        max_length=10
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "message",
            "user"
        )

    def __str__(self):

        return f"{self.user.username} reacted {self.emoji}"