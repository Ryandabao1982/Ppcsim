from rest_framework import serializers
from .models import CoachInsightsLog, Challenge, StudentChallengeProgress
from campaigns.serializers import CampaignSerializer, AdGroupSerializer, KeywordSerializer # For potential nested display

class CoachInsightsLogSerializer(serializers.ModelSerializer):
    # To show names instead of IDs for related entities if they are present
    related_campaign_name = serializers.CharField(source='related_campaign.name', read_only=True, allow_null=True)
    related_ad_group_name = serializers.CharField(source='related_ad_group.name', read_only=True, allow_null=True)
    related_keyword_text = serializers.CharField(source='related_keyword.text', read_only=True, allow_null=True)

    class Meta:
        model = CoachInsightsLog
        fields = [
            'id', 'user', 'simulated_week_start_date', 'insight_type',
            'generated_message', 'is_read', 'created_at',
            'related_campaign', 'related_campaign_name',
            'related_ad_group', 'related_ad_group_name',
            'related_keyword', 'related_keyword_text',
            'related_search_term_text'
        ]
        read_only_fields = ('user', 'created_at') # User is set based on authenticated user typically

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'id', 'name', 'description', 'objective_text',
            'difficulty_level', 'simulated_weeks_duration',
            'starting_conditions_json', # Consider if this should be exposed or just used internally
            'success_criteria_json',    # Same consideration for this
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

class StudentChallengeProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    challenge_name = serializers.CharField(source='challenge.name', read_only=True)
    challenge_description = serializers.CharField(source='challenge.description', read_only=True)
    challenge_objective = serializers.CharField(source='challenge.objective_text', read_only=True)

    class Meta:
        model = StudentChallengeProgress
        fields = [
            'id', 'user', 'user_email', 'challenge', 'challenge_name', 'challenge_description', 'challenge_objective',
            'status', 'start_sim_date', 'outcome_determination_date',
            'progress_details_json', 'last_updated_at'
        ]
        read_only_fields = ('user', 'challenge', 'last_updated_at', 'outcome_determination_date')
        # status might be updatable by system, start_sim_date set on creation.
        # progress_details_json updated by system.

    def to_representation(self, instance):
        """Add challenge duration to the representation."""
        representation = super().to_representation(instance)
        representation['challenge_duration_weeks'] = instance.challenge.simulated_weeks_duration

        # Calculate weeks passed if challenge is active
        if instance.status == 'active' and instance.start_sim_date:
            # This needs current_sim_date from context, which is tricky in serializer.
            # Better to calculate this in the view or as a model property if it needs current date.
            # For now, just showing start date.
            pass
        return representation
