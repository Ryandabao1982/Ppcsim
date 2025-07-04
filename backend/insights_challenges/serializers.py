from rest_framework import serializers
from .models import CoachInsightsLog, Challenge, StudentChallengeProgress
# from campaigns.serializers import CampaignSerializer, AdGroupSerializer, KeywordSerializer # Not strictly needed for current fields

class CoachInsightsLogSerializer(serializers.ModelSerializer):
    # To show names instead of IDs for related entities if they are present
    related_campaign_name = serializers.CharField(source='related_campaign.name', read_only=True, allow_null=True)
    related_ad_group_name = serializers.CharField(source='related_ad_group.name', read_only=True, allow_null=True)
    related_keyword_text = serializers.CharField(source='related_keyword.text', read_only=True, allow_null=True)
    # user_email = serializers.EmailField(source='user.email', read_only=True) # User ID is already present

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
        read_only_fields = ('user', 'created_at', 'simulated_week_start_date',
                            'insight_type', 'generated_message', 'related_campaign',
                            'related_ad_group', 'related_keyword', 'related_search_term_text')
        # `is_read` is the only field typically updated by user action via a specific endpoint.

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'scenario_details',
            'objective_summary', 'level',
            'product_context_asins',
            'scenario_constraints_json',
            'success_criteria', # Exposing the structured JSON criteria
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

class StudentChallengeProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    challenge_description = serializers.CharField(source='challenge.description', read_only=True)
    challenge_objective_summary = serializers.CharField(source='challenge.objective_summary', read_only=True)
    challenge_level = serializers.CharField(source='challenge.level', read_only=True)

    # Add challenge time limit from success_criteria to the representation
    challenge_time_limit_weeks = serializers.SerializerMethodField()

    class Meta:
        model = StudentChallengeProgress
        fields = [
            'id', 'user', 'user_email',
            'challenge', 'challenge_title', 'challenge_description', 'challenge_objective_summary', 'challenge_level', 'challenge_time_limit_weeks',
            'status', 'start_time', 'completion_time',
            'progress_details', 'last_updated_at'
        ]
        read_only_fields = ('user', 'challenge', 'last_updated_at', 'completion_time', 'start_time', 'status', 'progress_details')
        # Most fields are system-updated based on actions or checks.

    def get_challenge_time_limit_weeks(self, obj: StudentChallengeProgress) -> Optional[int]:
        """Extracts time_limit_weeks from the challenge's success_criteria."""
        if obj.challenge and isinstance(obj.challenge.success_criteria, dict):
            return obj.challenge.success_criteria.get('time_limit_weeks')
        return None

# No specific StartChallengeSerializer needed if only challenge ID from URL is used.
# If request body parameters were required for starting a challenge, one would be defined here.
