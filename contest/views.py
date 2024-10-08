from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from .models import Contest, Question, Option, Participant, Leaderboard, Submission
from .serializers import ContestSerializer, QuestionSerializer, OptionSerializer, ParticipantSerializer, SubmissionSerializer
from rest_framework.decorators import action
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

# Create your views here.




class ContestViewSet(ModelViewSet):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer


    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.prefetch_related('leaderboards')


    def create(self, request, *args, **kwargs):
        print('data in request data ==',request.data)
        return super().create(request, *args, **kwargs)



    @action(detail=True, methods=['post'], url_path='participate')
    def participate(self, request, pk=None):
        contest = self.get_object()
        user = request.user

        # if contest.status != 'ongoing':
        #     return Response({'error' : 'Contest is is not active for participation'}, status=status.HTTP_400_BAD_REQUEST)
        

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
            
            participant = get_object_or_404(Participant, id=participant_id)
            question = get_object_or_404(Question, id=question_id)
            selected_option = get_object_or_404(Option, id=selected_option_id)
            print('participant :',participant)
            print('question :',question)
            print('seleced option : ',selected_option)
        except :
            return Response({'detail' : 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        contest = participant.contest
        current_time = now()
        allowed_time = participant.created_at + contest.time_limit
        print('time limit ==',contest.time_limit)
        print('allowed time ==',allowed_time)


        if (current_time > allowed_time):
            return Response({'detail' : 'Time limit exceeded. Cannot submit the answer'}, status=status.HTTP_307_TEMPORARY_REDIRECT)
        

        if Submission.objects.filter(participant=participant, question=question).exists():
            return Response({'info' : 'You have already submitted this question'}, status=status.HTTP_400_BAD_REQUEST)


        is_correct = selected_option.is_correct
        print('is corrent',is_correct)

        submission = Submission.objects.create(
            participant=participant,
            question = question,
            selected_option = selected_option,
            is_correct = is_correct
        )

        if is_correct:
            print('total qeustion',contest.total_questions)
            print('max point',contest.max_points)
            points = (contest.max_points) / (contest.total_questions)
            print('user ppoint', points)
            participant.score += points
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
        participant.time_taken = now() - participant.created_at
        participant.save()

        update_leaderboard(participant.contest)


        return Response({'detail' : 'Contest completed successfully '}, status=status.HTTP_200_OK)


def update_leaderboard(contest):
    print('leaderboard updated ....')
    participants = Participant.objects.filter(contest=contest).order_by('-score')
    for rank, participant in enumerate(participants, start=1):
        Leaderboard.objects.update_or_create(
            contest=contest,
            user=participant.user,
            defaults={'score': participant.score, 'rank': rank}
        )



