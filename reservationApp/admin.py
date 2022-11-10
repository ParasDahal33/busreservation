from django.contrib import admin
from reservationApp.models import Category, Location, Bus, Schedule, Booking
# Register your models here.


class CategoryAdminView(admin.ModelAdmin):
    list_display = ('name', 'description', 'status', 'date_created')
    list_per_page = 25
admin.site.register(Category, CategoryAdminView)


class LocationAdminView(admin.ModelAdmin):
    list_display = ('location', 'status', 'date_created', 'date_updated')
    
admin.site.register(Location, LocationAdminView)


class BusAdminView(admin.ModelAdmin):
    list_display = ('category', 'bus_number', 'seats',
                    'status', 'date_created', 'date_updated')
    list_per_page = 25
admin.site.register(Bus, BusAdminView)


class ScheduleAdminView(admin.ModelAdmin):
    list_display = ('code', 'bus', 'depart', 'destination',
                    'schedule', 'fare', 'status', 'date_created')
    list_per_page = 25
admin.site.register(Schedule, ScheduleAdminView)


class BookingAdminView(admin.ModelAdmin):
    list_display = ('code', 'name', 'schedule', 'seats', 'status',
                    'date_created', 'date_updated', 'total_payable')
    list_per_page = 25
admin.site.register(Booking, BookingAdminView)
