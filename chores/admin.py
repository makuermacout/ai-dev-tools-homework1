from django.contrib import admin
from .models import Household, HouseholdMember, ChoreDefinition, ChoreInstance


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'rotation_order')
    list_filter = ('household',)
    search_fields = ('user__username', 'household__name')


@admin.register(ChoreDefinition)
class ChoreDefinitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'household', 'frequency', 'is_active')
    list_filter = ('household', 'frequency', 'is_active')
    search_fields = ('title', 'description')


@admin.register(ChoreInstance)
class ChoreInstanceAdmin(admin.ModelAdmin):
    list_display = ('chore_definition', 'doer', 'inspector', 'status', 'due_date')
    list_filter = ('status', 'due_date', 'chore_definition__household')
    search_fields = ('chore_definition__title', 'doer__username', 'inspector__username')