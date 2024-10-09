from rest_framework import serializers 
from .models import Contest, Question, Option, Participant, Submission, Leaderboard
from course.serializers import CategorySerializer
from users.api.user_serializers import UserSerializers
from course.models import Category
from django.utils import timezone


class OptionSerializer(serializers.ModelSerializer):
    """Serializer for the Option model."""

    class Meta:
        model = Option
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for the Question model, including options."""

    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = '__all__'

    
    def validate(self, attrs):
        """Validate the question text and options."""
        question = attrs.get('question_text').strip()
        option_data = attrs.get('options', [])

        # Ensure the question text is valid
        if not question:
            raise serializers.ValidationError({'Question': 'Not a valid question'})

        # Ensure there are at least 2 and no more than 4 options
        if len(option_data) < 2:
            raise serializers.ValidationError({'Option': 'A question must have at least 2 options'})
        if len(option_data) > 4:
            raise serializers.ValidationError({"Option": 'A question must have at most 4 options'})

        # Ensure at least one option is marked as correct
        correct_option = [option for option in option_data if option.get('is_correct') is True]
        if not correct_option:
            raise serializers.ValidationError({"Option": "At least one option must be correct"})

        return attrs

    def create(self, validated_data):
        """Create a new question and associated options."""
        options_data = validated_data.pop('options', [])
        contest = validated_data.get('contest', None)
        question = Question.objects.create(**validated_data)

        # Update the contest total questions if applicable
        if contest:
            contest.total_questions += 1
            contest.save()

        # Create associated options for the question
        for option in options_data:
            Option.objects.create(question=question, **option)

        return question

    def update(self, instance, validated_data):
        """Update an existing question and its options."""
        option_data = validated_data.pop('options', [])
        instance.question_text = validated_data.get('question_text', instance.question_text)
        instance.save()

        # Delete existing options and create new ones
        instance.options.all().delete()
        for option in option_data:
            option.pop('question', None)  
            Option.objects.create(question=instance, **option) 

        return instance


class ContestSerializer(serializers.ModelSerializer):
    """Serializer for the Contest model, including related questions and participants."""

    questions = QuestionSerializer(many=True, required=False)
    category = CategorySerializer(read_only=True)
    participants = UserSerializers(many=True, read_only=True)
    participant_id = serializers.SerializerMethodField(read_only=True)
    category_id = serializers.CharField(write_only=True)
    is_participated = serializers.SerializerMethodField()
    leaderboard = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = '__all__'

    def validate(self, attrs):
        """Validate the contest fields."""
        name = attrs.get('name').strip()
        description = attrs.get('description').strip()
        category_id = attrs.get('category_id')
        difficulty_level = attrs.get('difficulty_level', '')
        time_limit = attrs.get('time_limit', '')

        # Validate contest name
        if not name:
            raise serializers.ValidationError({'Name': 'Not a valid Name'})

        # Check for unique contest name
        if self.instance:
            if Contest.objects.filter(name=name).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({"Name": "Contest name already exists."})
        else:
            if Contest.objects.filter(name=name).exists():
                raise serializers.ValidationError({"Name": "Contest name already exists."})

        # Validate other fields
        if not description:
            raise serializers.ValidationError({'Description': "Not a valid Description"})
        if not difficulty_level:
            raise serializers.ValidationError({'Difficulty Level': 'Please select a difficulty level'})
        if not time_limit:
            raise serializers.ValidationError({"Time limit": 'Please specify a time limit for the contest'})

        # Validate category
        try:
            category = Category.objects.get(id=category_id)
            attrs['category'] = category
        except Category.DoesNotExist:
            raise serializers.ValidationError('Invalid category id; category does not exist')

        # Validate start and end times
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError('The start time must be before the end time')

        # Validate max points
        max_points = attrs.get('max_points', 0)
        if max_points <= 0:
            raise serializers.ValidationError('Max points must be a positive number')

        # Validate time limit
        if time_limit and time_limit.total_seconds() <= 0:
            raise serializers.ValidationError('Time limit must be greater than 0')

        return attrs

    def create(self, validated_data):
        """Create a new contest."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'tutor_profile'):
                tutor = user.tutor_profile
                validated_data['tutor'] = tutor
            else:
                raise serializers.ValidationError("Tutor id is not valid")

        # Remove category_id and set contest status
        validated_data.pop('category_id', None)
        self.set_contest_status(validated_data)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update an existing contest."""
        self.set_contest_status(validated_data)
        return super().update(instance, validated_data)

    def get_participant_id(self, obj):
        """Get the participant ID of the authenticated user for the contest."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                try:
                    participant = Participant.objects.get(user=user, contest=obj)
                    return participant.id
                except Participant.DoesNotExist:
                    return None
            else:
                return None
        return None
    
    def get_is_participated(self, obj):
        """Check if the authenticated user has participated in the contest."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if user.is_authenticated:
                return Participant.objects.filter(contest=obj, user=user).exists()
        return False

    def get_leaderboard(self, obj):
        """Retrieve the leaderboard for the contest."""
        leaderboard = Leaderboard.objects.filter(contest=obj).order_by('rank')
        return LeaderboardSerializer(leaderboard, many=True).data

    def set_contest_status(self, validated_data):
        """Set the status of the contest based on the current time."""
        current_time = timezone.now()
        start_time = validated_data.get('start_time')
        end_time = validated_data.get('end_time')

        if start_time > current_time:
            validated_data['status'] = 'scheduled'
        elif start_time <= current_time < end_time:
            validated_data['status'] = 'ongoing'
        else:
            validated_data['status'] = 'finished'


class ParticipantSerializer(serializers.ModelSerializer):
    """Serializer for the Participant model."""

    class Meta:
        model = Participant
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for the Submission model."""

    class Meta:
        model = Submission
        fields = '__all__'


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for the Leaderboard model, including user data and contest details."""

    user = UserSerializers(read_only=True)
    contest_data = serializers.SerializerMethodField()

    class Meta:
        model = Leaderboard
        fields = '__all__'
        depth = 1

    def contest_data(self, obj):
        """Retrieve basic contest data for leaderboard entry."""
        contest = obj.contest
        return {
            "id": contest.id,
            "name": contest.name
        }
