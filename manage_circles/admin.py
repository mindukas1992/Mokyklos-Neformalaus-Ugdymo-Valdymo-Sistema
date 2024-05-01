from django.contrib import admin
from .models import Parent, Child, Club, Session, Enrollment


class ChildAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'child_age', 'school', 'classroom', 'parent')
    search_fields = ('first_name', 'last_name', 'child_age', 'school', 'classroom', 'parent')


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type')
    search_fields = ('name', 'activity_type')


class SessionAdmin(admin.ModelAdmin):
    list_display = ('club', 'day_of_week', 'start_time', 'end_time', 'group')
    search_fields = ('club', 'day_of_week', 'start_time', 'end_time', 'group')


class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('child', 'session', 'registration_date')
    search_fields = ('child', 'session', 'registration_date')


class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'phone_number', 'address')
    search_fields = ('user', 'first_name', 'last_name', 'email', 'phone_number', 'address')


admin.site.register(Parent, ParentAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(Club, ClubAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
