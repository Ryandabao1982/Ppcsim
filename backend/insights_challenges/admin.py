from django.contrib import admin
from .models import CoachInsightsLog, Challenge, StudentChallengeProgress

@admin.register(CoachInsightsLog)
class CoachInsightsLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'simulated_week_start_date',
        'insight_type',
        'related_campaign_display',
        'is_read',
        'created_at'
    )
    list_filter = ('insight_type', 'is_read', 'simulated_week_start_date', 'user__email')
    search_fields = ('user__email', 'generated_message', 'related_campaign__name', 'related_search_term_text')
    readonly_fields = ('created_at',)
    list_select_related = ('user', 'related_campaign') # Optimize queries

    def related_campaign_display(self, obj):
        return obj.related_campaign.name if obj.related_campaign else None
    related_campaign_display.short_description = 'Campaign'
    related_campaign_display.admin_order_field = 'related_campaign__name'


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'is_active', 'created_at') # Updated fields
    list_filter = ('level', 'is_active') # Updated field
    search_fields = ('title', 'description', 'objective_summary') # Updated fields
    readonly_fields = ('created_at', 'updated_at')

    # Could use a custom widget or validation for JSONFields if needed,
    # e.g., django-jsoneditor or similar, but for admin, raw JSON is often acceptable.


@admin.register(StudentChallengeProgress)
class StudentChallengeProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'start_time', 'completion_time', 'last_updated_at') # Updated fields
    list_filter = ('status', 'challenge__title', 'user__email') # Updated field challenge__title
    search_fields = ('user__email', 'challenge__title') # Updated field challenge__title
    readonly_fields = ('last_updated_at',)
    date_hierarchy = 'start_time' # Updated field
    list_select_related = ('user', 'challenge') # Optimize queries
