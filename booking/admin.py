from django.contrib import admin

# Register your models here.

from booking.models import (Booking, BookingAllotment, BookingTransfer,
                            BookingExtra)


class BookingAllotmentInline(admin.TabularInline):
    model = BookingAllotment
    classes = ('collapse',)


class BookingTransferInline(admin.TabularInline):
    model = BookingTransfer
    classes = ('collapse',)


class BookingExtraInline(admin.TabularInline):
    model = BookingExtra
    classes = ('collapse',)


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    search_fields = ['name', 'reference']
    inlines = [BookingAllotmentInline,
               BookingTransferInline,
               BookingExtraInline]


admin.site.register(Booking, BookingAdmin)
