from django.contrib import admin
from .models import ClassName, Student
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import User 
# Register your models here.
class StudentInline(admin.StackedInline):
	model = Student
	can_delete = False

class StudentUserAdmin(UserAdmin):
	def add_view(self, *arg, **kwargs):
		self.inlines = [StudentInline]
		return super(StudentUserAdmin, self).add_view(*arg, **kwargs)
		
	def change_view(self, *arg, **kwargs):
		self.inlines = [StudentInline]
		return super(StudentUserAdmin, self).change_view(*arg, **kwargs)
	
admin.site.unregister(User)
admin.site.register(User, StudentUserAdmin)
admin.site.register(ClassName)