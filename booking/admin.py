from django.contrib import admin

# Register your models here.

from booking.models import Booking, BookingAllotment


class BookingAllotmentInline(admin.TabularInline):
    model = BookingAllotment
    classes = ('collapse',)


class BookingAdmin(admin.ModelAdmin):
    model = Booking
    inlines = [BookingAllotmentInline]

admin.site.register(Booking, BookingAdmin)
