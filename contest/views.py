from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .models import Contest, Question, Option, Participant, Leaderboard, Submission
from .serializers import ContestSerializer, QuestionSerializer, OptionSerializer, ParticipantSerializer, SubmissionSerializer
from rest_framework.decorators import action
from django.utils.timezone import now

# Create your views here.




class ContestViewSet(ModelViewSet):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer


    @action(detail=True, methods=['post'], url_path='participate')
    def participate(self, request, pk=None):
        contest = self.get_object()
        user = request.user

        participant, created = Participant.objects.get_or_create(contest=contest, user=user)

        if not created:
            return Response({'error' : "Your're already participated this contest"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ParticipantSerializer(participant)

        return Response(serializer.data)
    



class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class SubmissionViewSet(ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

    def create(self, request, *args, **kwargs):
        participant_id = request.data.get('participant_id', '')
        question_id = request.data.get('question_id', '')
        selected_option_id = request.data.get('selected_option_id', '')
        print('participant id :',participant_id)
        print('question id :',question_id)
        print('seleced option id : ',selected_option_id)

        try:
            participant = Participant.objects.get(id=participant_id)
            question = Question.objects.get(id=question_id)
            selected_option = Option.objects.get(id=selected_option_id)
            print('participant :',participant)
            print('question :',question)
            print('seleced option : ',selected_option)
        except (Participant.DoesNotExist, Question.DoesNotExist, Option.DoesNotExist):
            return Response({'detail' : 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        

        is_correct = selected_option.is_correct
        print('is corrent',is_correct)

        if Submission.objects.filter(participant=participant, question=question).first():
            return Response({'info' : 'You have already submitted this question'}, status=status.HTTP_400_BAD_REQUEST)

        submission = Submission.objects.create(
            participant=participant,
            question = question,
            selected_option = selected_option,
            is_correct = is_correct
        )

        if is_correct:
            participant.score += 1
            participant.save()

        serializer = SubmissionSerializer(submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'], url_path='stop_or_complete')
    def stop_or_complete(self, request):
        participant_id = request.data.get('participant_id', '')

        try:
            participant = Participant.objects.get(id=participant_id)
        except Participant.DoesNotExist:
            return Response({'detail' : "Participant not found" }, status=status.HTTP_400_BAD_REQUEST)
        

        participant.completed_at = now()
        participant.save()

        return Response({'detail' : 'Contest completed successfully '}, status=status.HTTP_200_OK)



