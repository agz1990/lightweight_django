from datetime import date
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.reverse import reverse
from .models import Sprint, Task

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', User.USERNAME_FIELD, 'full_name', 'is_active', 'links')

    def get_links(self, obj):
        request = self.context['request']
        username = obj.get_username()
        return {
            'self': reverse('board:user-detail',
                            kwargs={User.USERNAME_FIELD: username}, request=request),
        }


class SprintSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = Sprint
        fields = ('id', 'name', 'description', 'end', 'links')

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('board:sprint-detail',
                            kwargs={'pk': obj.pk}, request=request),
        }

    def validate_end(self, value):
        end_date = value
        new = not self.instance
        changed = self.instance and self.instance.end != end_date
        if (new or changed) and (end_date < date.today()):
            msg = _('End date cannot be in the past.')
            raise serializers.ValidationError(msg)

        return value


class TaskSerializer(serializers.ModelSerializer):
    assigned = serializers.SlugRelatedField(slug_field=User.USERNAME_FIELD,
                                            required=False, read_only=True)
    status_disply = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'name', 'description', 'sprint', 'status', 'status_disply', 'order',
                  'assigned', 'started', 'due', 'completed', 'links')

    def get_status_disply(self, obj):
        return obj.get_status_display()

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('board:task-detail', kwargs={'pk': obj.pk}, request=request),
        }

        if obj.sprint_id:
            links['sprint'] = reverse('board:sprint-detail',
                                      kwargs={'pk': obj.sprint_id}, request=request)

        if obj.assigned:
            links['assigned'] = reverse('board:user-detail',
                                        kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)

        return links

    def validated_sprint(self, sprint):

        if self.instance and self.instance.pk:
            if sprint != self.instance.sprint:
                if self.instance.status == Task.STATUS_DONE:
                    msg = _('Cannot change the sprint of complete task.')
                    raise serializers.ValidationError(msg)
                if sprint and sprint.end < date.today():
                    msg = _('Cannot assign tasks to past sprints.')
                    raise serializers.ValidationError(msg)

            else:
                if sprint and sprint.end < date.today():
                    msg = _('Cannot add task to past sprints')
                    raise serializers.ValidationError(msg)

        return sprint

    def validate(self, attrs):
        sprint = attrs.get('sprint')
        status = int(attrs.get('status'))
        started = attrs.get('started')
        completed = attrs.get('completed')

        if not sprint and status != Task.STATUS_TODO:
            msg = _('Backlog tasks must have "Not Started" status.')
            raise serializers.ValidationError(msg)
        if started and status == Task.STATUS_TODO:
            msg = _('Started date cannot be set for not started tasks.')
            raise serializers.ValidationError(msg)
        if completed and status != Task.STATUS_DONE:
            msg = _('Completed date cannot be set for uncompleted tasks.')
            raise serializers.ValidationError(msg)
        return attrs
