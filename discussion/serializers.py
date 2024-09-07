from .models import Discussion, Comment
from rest_framework import  serializers
from users.api.user_serializers import UserSerializers




class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializers(read_only=True)
    replies = serializers.SerializerMethodField()  
    is_my_comment = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    
    
    def get_is_my_comment(self, obj):
        user = self.context.get('request').user 
        return user == obj.user
    




class DiscussionSerializer(serializers.ModelSerializer):
    upvote_count = serializers.IntegerField( read_only=True)
    downvote_count = serializers.IntegerField( read_only=True)
    commented_discussion  = serializers.SerializerMethodField(read_only=True)
    user = UserSerializers(read_only = True)
    is_my_discussion = serializers.SerializerMethodField(read_only=True)
    is_upvoted = serializers.SerializerMethodField(read_only=True)
    is_downvoted = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Discussion
        fields = '__all__'
        extra_kwargs = {
            'upvoted_count' : {'required' : False},
            'downvoted_count' : {'required' : False}
        }


    def validate(self, data):
        title = data.get('title', '').strip()
        description = data.get('description', '')
        photo = data.get('photo', None)


        if not title:
            raise serializers.ValidationError({"title": "Title can't be blank"})
        
        if description and not description.strip():
            raise serializers.ValidationError({"description": "Description can't be blank"})

        # if photo and hasattr(photo, 'name'):
        #     raise ValidationError({'photo' : 'Invalid Image'})
        
        return data

    def create(self, validated_data):
        print('validating data : ===',validated_data)
        
        discussion = super().create(validated_data)

        
        return discussion


    def get_commented_discussion(self, obj):
        return CommentSerializer(obj.commented_discussion.filter(parent=None), many=True, context=self.context).data
    

    def get_is_my_discussion(self, obj):
        user = self.context['request'].user
        return obj.user == user
    
    def get_is_upvoted(self, obj):
        user = self.context['request'].user
        return user in obj.upvoted_by.all()
    
    def get_is_downvoted(self, obj):
        user = self.context['request'].user
        return user in obj.downvoted_by.all()