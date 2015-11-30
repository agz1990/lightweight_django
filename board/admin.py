from django.contrib import admin
from board.models import Sprint, Task


# Register your models here.
class SprintModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'end')

class TaskModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'sprint',
                    'assigned', 'started', 'status', 'due',
                    'completed')

admin.site.register(Sprint, SprintModelAdmin)
admin.site.register(Task, TaskModelAdmin)