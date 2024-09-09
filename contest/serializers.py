from rest_framework import serializers 
from .models import Contest, Question, Option, Participant, Submission, Leaderboard
from course.serializers import CategorySerializer




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

    class Meta:
        model = Contest
        fields = '__all__'


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