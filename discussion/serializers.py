from .models import Discussion, Comment
from rest_framework import  serializers
from users.api.user_serializers import UserSerializers



class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling comments. Includes user, replies, and methods to determine
    if the comment belongs to the current user.
    """
    user = UserSerializers(read_only=True)
    replies = serializers.SerializerMethodField()  # For nested comment replies
    is_my_comment = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def get_replies(self, obj):
        """
        Retrieves replies for a comment if they exist.
        """
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def get_is_my_comment(self, obj):
        """
        Returns True if the current user is the owner of the comment.
        """
        user = self.context.get('request').user
        return user == obj.user


class DiscussionSerializer(serializers.ModelSerializer):
    """
    Serializer for handling discussions. Includes user, upvote/downvote counts, 
    and methods to determine if the discussion is upvoted, downvoted, or belongs to the current user.
    """
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
        """
        Validates the input data for creating or updating a discussion. Ensures
        the title is not empty and the description has meaningful content.
        """
        title = data.get('title', '').strip()
        description = data.get('description', '')
        photo = data.get('photo', None)


        if not title:
            raise serializers.ValidationError({"title": "Title can't be blank"})
        
        if description and not description.strip():
            raise serializers.ValidationError({"description": "Description can't be blank"})

        # Custom validation for photo can be added here if needed
        # if photo and hasattr(photo, 'name'):
        #     raise ValidationError({'photo': 'Invalid Image'})

        return data

    def create(self, validated_data):
        """
        Custom logic for creating a new discussion. Uses the validated data to create a discussion.
        """
        discussion = super().create(validated_data)
        return discussion

    def get_commented_discussion(self, obj):
        """
        Retrieves top-level comments (those without a parent) for the discussion.
        """
        return CommentSerializer(obj.commented_discussion.filter(parent=None), many=True, context=self.context).data

    def get_is_my_discussion(self, obj):
        """
        Returns True if the current user is the owner of the discussion.
        """
        user = self.context['request'].user
        return obj.user == user

    def get_is_upvoted(self, obj):
        """
        Returns True if the current user has upvoted the discussion.
        """
        user = self.context['request'].user
        return user in obj.upvoted_by.all()

    def get_is_downvoted(self, obj):
        """
        Returns True if the current user has downvoted the discussion.
        """
        user = self.context['request'].user
        return user in obj.downvoted_by.all()
