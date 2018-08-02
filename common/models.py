
from django.conf import settings
from django.db import models
from django.utils import timezone

class RecentLink(models.Model):
    class Meta:
        verbose_name = 'Recent Entry'
        verbose_name_plural = 'Recents Entries'
        unique_together = (('user', 'link_url'),)
        index_together = (('user', 'link_time'),)
        ordering = ('user', '-link_time',)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    link_time = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    link_label = models.CharField(max_length=250)
    link_url = models.CharField(max_length=250)
    link_icon = models.CharField(max_length=50)
    
    def __str__(self):
        return self.link_label
