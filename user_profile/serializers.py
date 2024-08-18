from rest_framework import serializers
from .models import Tutor, Education, Experience, Skill
from users.api.user_serializers import UserSerializers
from users.models import CustomUser


from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None  # or handle the error as needed


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['highest_qualification', 'name_of_institution', 'year_of_qualification']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['company_name', 'position', 'start_date', 'end_date']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill_name']



class TutorSerializer(serializers.ModelSerializer):
    education = serializers.ListField(child=serializers.JSONField(), required=False, write_only=True)
    experiences = serializers.ListField(child=serializers.JSONField(), required=False, write_only=True)
    skills = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    user = UserSerializers(read_only=True) 
    
    class Meta:
        model = Tutor
        fields = ['id', 'user', 'cv', 'display_name', 'headline', 'status',  'education', 'experiences', 'skills' ]
        
    
    def create(self, validated_data):
        print('validated data ',validated_data)
        
        education_data = validated_data.pop('education', [])
        experiences_data = validated_data.pop('experiences', [])
        skills_data = validated_data.pop('skills', [])

        print('education == ',education_data)
        print('experience == ',experiences_data)
        print('skiils == ',skills_data)

        print('after popping validating data', validated_data)

        tutor = Tutor.objects.create(**validated_data)
        print('tutor id',tutor)

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

        for one_skill in skills_data:
            for skill in one_skill:
                print('skillllllllllll ========', skill)
                Skill.objects.create(
                    tutor=tutor,
                    skill_name=skill
                )

        tutor.refresh_from_db()
        return tutor

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['education'] = EducationSerializer(instance.education.all(), many=True).data
        representation['experiences'] = ExperienceSerializer(instance.experiences.all(), many=True).data
        representation['skills'] = SkillSerializer(instance.skills.all(), many=True).data
        return representation
