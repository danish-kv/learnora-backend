from rest_framework import serializers
from .models import Tutor, Education, Experience, Skill
from users.api.user_serializers import UserSerializers
from datetime import datetime


def parse_date(date_str):
    """Helper function to parse a date string in the format '%Y-%m-%d'. Returns None if the format is invalid."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None  


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for Education model."""
    class Meta:
        model = Education
        fields = ['id', 'highest_qualification', 'name_of_institution', 'year_of_qualification']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for Experience model."""
    class Meta:
        model = Experience
        fields = ['id', 'company_name', 'position', 'start_date', 'end_date']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model."""
    class Meta:
        model = Skill
        fields = ['id', 'skill_name']


class TutorSerializer(serializers.ModelSerializer):
    """
    Serializer for Tutor model with nested serializers for education, experience, and skills.
    This serializer also includes a custom field for total_courses and handles complex creation and updating logic.
    """
    education = serializers.ListField(child=serializers.JSONField(), required=False, write_only=True)
    experiences = serializers.ListField(child=serializers.JSONField(), required=False, write_only=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)
    userId = serializers.CharField(write_only=True)
    user = UserSerializers(required=False) 
    total_courses = serializers.SerializerMethodField()

    class Meta:
        model = Tutor
        fields = ['id', 'user', 'userId', 'cv', 'display_name', 'headline', 'status',  'education', 'experiences', 'skills', 'total_courses' ]

    def get_total_courses(self, obj):
        """Returns the total number of courses instructed by the tutor."""
        return obj.instructed_courses.count()

    def create(self, validated_data):
        """
        Custom create method to handle nested relationships for education, experiences, and skills.
        Also associates the tutor with a user based on userId.
        """
        education_data = validated_data.pop('education', [])
        experiences_data = validated_data.pop('experiences', [])
        skills_data = validated_data.pop('skills', [])
        user = validated_data.get('userId')

        # Retrieve or create the tutor profile for the user
        tutor = Tutor.objects.get(user=user)
        tutor.cv = validated_data.get('cv', tutor.cv)
        tutor.display_name = validated_data.get('display_name', tutor.display_name)
        tutor.headline = validated_data.get('headline', tutor.headline)
        tutor.status = Tutor.REQUESTED
        tutor.save()

        # Process education data
        for edu_list in education_data:
            for edu in edu_list:
                Education.objects.create(
                    tutor=tutor,
                    highest_qualification=edu.get('highestQualification', ''),
                    name_of_institution=edu.get('institute', ''),
                    year_of_qualification=parse_date(edu.get('year', ''))
                )

        # Process experience data
        for exp_list in experiences_data:
            for exp in exp_list:
                Experience.objects.create(
                    tutor=tutor,
                    company_name=exp.get('workplace', ''),
                    position=exp.get('position', ''),
                    start_date=parse_date(exp.get('startDate', '')),
                    end_date=parse_date(exp.get('endDate', ''))
                )

        # Process skills data
        for skill in skills_data:
            Skill.objects.create(
                tutor=tutor,
                skill_name=skill
                )
            
        # Reload the tutor instance with fresh data
        tutor.refresh_from_db()
        return tutor

    def to_representation(self, instance):
        """
        Custom representation of the tutor object to include education, experiences, and skills details.
        """
        representation = super().to_representation(instance)
        representation['education'] = EducationSerializer(instance.education.all(), many=True).data
        representation['experiences'] = ExperienceSerializer(instance.experiences.all(), many=True).data
        representation['skills'] = SkillSerializer(instance.skills.all(), many=True).data
        return representation

    def update(self, instance, validated_data):
        """
        Custom update method to handle nested user updates and tutor profile updates.
        """
        user_data = validated_data.pop('user', None)

        # Update the tutor instance
        instance = super().update(instance, validated_data)

        # If user data is provided, update the associated user
        if user_data:
            user = instance.user
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
        return instance


class CourseSalesSerializer(serializers.Serializer):
    """
    Serializer for representing course sales data.
    Includes the course ID, course title, total sales, and total amount.
    """
    course_id = serializers.IntegerField()
    course_title = serializers.CharField(source='course__title')
    total_sales = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2) 
