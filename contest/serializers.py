from rest_framework import serializers 
from .models import Contest, Question, Option, Participant, Submission, Leaderboard
from course.serializers import CategorySerializer
from users.api.user_serializers import UserSerializers



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)

        for option in options_data:
            print(option)
            Option.objects.create(question=question, **option)
        return question



class ContestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    category = CategorySerializer(read_only=True)
    participants = UserSerializers(many=True, read_only=True)
    participant_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Contest
        fields = '__all__'

    
    def get_participant_id(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            try:
                participant  = Participant.objects.get(user=user, contest=obj)
                return participant.id
            except Participant.DoesNotExist:
                return None
        return None


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = '__all__'