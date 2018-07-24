
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
    link_label = models.CharField(max_length=50)
    link_url = models.CharField(max_length=250)
    link_icon = models.CharField(max_length=50)
    
    def __str__(self):
        return self.link_label

    @classmethod
    def register_link(cls, user, label, url, icon):
        cls.objects.update_or_create(
            user_id=user.pk,
            link_url=url,
            defaults={
                'user_id': user.pk,
                'link_time': timezone.now,
                'link_label': label,
                'link_url': url,
                'link_icon': icon,},)

    def get_example_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        if self.content_type and self.object_id:
            url_name = 'admin:%s_%s_change' % (self.content_type.app_label, self.content_type.model)
            try:
                return reverse(url_name, args=(quote(self.object_id),))
            except NoReverseMatch:
                pass
        return None
        """
