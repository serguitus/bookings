# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.forms import ValidationError
from django.utils import timezone

from common.middleware import get_current_organization


class Organization(models.Model):
    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=10, unique=True)
    restricted = models.BooleanField(default=False)


class Vinculation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)


class OrganizationAwareManager(models.Manager):
    def get_queryset(self):

        organization = get_current_organization()

        if organization is None or not organization.restricted:
            return super().get_queryset()

        return super().get_queryset().filter(organization__id=organization.id)


class OrganizationAwareModelMixin(models.Model):
    """
    An abstract base class model that provides a foreign key to an organization
    """
    class Meta:
        abstract = True

    organization = models.ForeignKey(Organization, models.CASCADE)

    objects = OrganizationAwareManager()
    objects_all = models.Manager()

    def __save_allowed__(self, user_organization):
        empty_organization = user_organization is None or self.organization is None
        return empty_organization or not user_organization.restricted or user_organization.id == self.organization.id

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # set organization data
        organization = get_current_organization
        if self.__save_allowed__(organization):
            if self.organization is None:
                self.organization = organization
        else:
            raise ValidationError("Invalid Save operation for User Org. %s and Model Org. %s" %(organization.short_name, self.organization.short_name) )

        # Call the super save() method.
        super(OrganizationAwareModelMixin, self).save(force_insert, force_update, using, update_fields)


class FillDataSaveModelMixin(models.Model):
    """
    An abstract base class model that provides a fill data method executed before saving
    """
    class Meta:
        abstract = True

    def fill_data(self):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.fill_data()
        # Call the super save() method.
        super(FillDataSaveModelMixin, self).save(force_insert, force_update, using, update_fields)


class ValidateSaveModelMixin(models.Model):
    """
    An abstract base class model that provides a validate method executed before saving
    """
    class Meta:
        abstract = True

    def validate(self):
        pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate()
        # Call the super save() method.
        super(ValidateSaveModelMixin, self).save(force_insert, force_update, using, update_fields)


class AtomicSaveModelMixin(models.Model):
    """
    An abstract base class model that provides atomic saving
    """
    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        with transaction.atomic(savepoint=False):
            # Call the super save() method.
            super(AtomicSaveModelMixin, self).save(force_insert, force_update, using, update_fields)


class RecentLink(models.Model):
    class Meta:
        verbose_name = 'Recent Entry'
        verbose_name_plural = 'Recents Entries'
        unique_together = (('user', 'link_url'),)
        index_together = (('user', 'link_time'),)
        ordering = ['user', '-link_time']

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
