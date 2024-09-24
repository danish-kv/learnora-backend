from rest_framework import serializers
from .models import Tutor, Education, Experience, Skill
from users.api.user_serializers import UserSerializers
from users.models import CustomUser


from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None  


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'highest_qualification', 'name_of_institution', 'year_of_qualification']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company_name', 'position', 'start_date', 'end_date']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill_name']



class TutorSerializer(serializers.ModelSerializer):
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
        return obj.instructed_courses.count()
    
    def create(self, validated_data):
        
        education_data = validated_data.pop('education', [])
        experiences_data = validated_data.pop('experiences', [])
        skills_data = validated_data.pop('skills', [])
        user = validated_data.get('userId', None)

        tutor = Tutor.objects.get(user=user)
        tutor.cv = validated_data.get('cv', tutor.cv)
        tutor.display_name = validated_data.get('display_name', tutor.display_name)
        tutor.headline = validated_data.get('headline', tutor.headline)
        tutor.status = Tutor.REQUESTED
        tutor.save()

        for edu_list in education_data:
            for edu in edu_list:
                Education.objects.create(
                    tutor=tutor,
                    highest_qualification=edu.get('highestQualification', ''),
                    name_of_institution=edu.get('institute', ''),
                    year_of_qualification=parse_date(edu.get('year', ''))
                )

        for exp_list in experiences_data:
            for exp in exp_list:
                Experience.objects.create(
                    tutor=tutor,
                    company_name=exp.get('workplace', ''),
                    position=exp.get('position', ''),
                    start_date=parse_date(exp.get('startDate', '')),
                    end_date=parse_date(exp.get('endDate', ''))
                )

        for skill in skills_data:
            Skill.objects.create(
                tutor=tutor,
                skill_name=skill
                )
            
        
        tutor.status = Tutor.REQUESTED
        tutor.save()

        tutor.refresh_from_db()
        return tutor

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['education'] = EducationSerializer(instance.education.all(), many=True).data
        representation['experiences'] = ExperienceSerializer(instance.experiences.all(), many=True).data
        representation['skills'] = SkillSerializer(instance.skills.all(), many=True).data
        return representation

    def update(self, instance, validated_data):
        print(validated_data)
        user_data = validated_data.pop('user', None)

        instance = super().update(instance, validated_data)
        
        if user_data:
            user = instance.user
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
        return instance
    