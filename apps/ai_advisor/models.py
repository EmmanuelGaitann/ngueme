from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    ROLE_USER      = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES   = [(ROLE_USER, 'Utilisateur'), (ROLE_ASSISTANT, 'Assistant')]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering     = ['created_at']
        verbose_name = 'Message chat'

    def __str__(self):
        return f'[{self.role}] {self.content[:60]}'


class AIReport(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_reports')
    content    = models.TextField()
    week_start = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['-created_at']
        unique_together = ('user', 'week_start')

    def __str__(self):
        return f'Rapport {self.user} — {self.week_start}'
