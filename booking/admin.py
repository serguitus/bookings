from django.contrib import admin

# Register your models here.

from booking.models import (Booking, BookingProvidedAllotment, BookingProvidedTransfer,
                            BookingProvidedExtra)


class BookingAllotmentInline(admin.TabularInline):
    model = BookingProvidedAllotment
    classes = ('collapse',)


class BookingTransferInline(admin.TabularInline):
    model = BookingProvidedTransfer
    classes = ('collapse',)


class BookingExtraInline(admin.TabularInline):
    model = BookingProvidedExtra
    classes = ('collapse',)


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    search_fields = ['name', 'reference']
    inlines = [BookingAllotmentInline,
               BookingTransferInline,
               BookingExtraInline]


admin.site.register(Booking, BookingAdmin)
