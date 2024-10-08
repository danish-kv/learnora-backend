from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
from .models import Category, Course, Module, StudentCourseProgress, Review, Transaction, Note
from users.models import CustomUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status, generics
from .serializers import CourseSerializer, CategorySerializer, ModuleSerializer, ReviewSerializer, NotesSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import get_object_or_404
from urllib.parse import urlencode
from datetime import datetime
from datetime import timedelta
from django.db import transaction
import json
import stripe
from base.custom_pagination_class import CustomPagination
from base.custom_permissions import IsAdmin, IsStudent, IsTutor
from rest_framework.permissions import AllowAny
from django.db.models import Q

# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.all().order_by('id')

        if user.is_anonymous or not user.is_authenticated :
            queryset = queryset.filter(Q(status='Approved') & Q(is_active = True))

        if user.is_staff:
            queryset = queryset.exclude(status='Requested')
        elif hasattr(user, 'role'):
            if user.role == 'student':

                queryset = queryset.filter(Q(status='Approved') & Q(is_active=True))
            elif user.role == 'tutor':
                queryset = queryset.exclude(Q(status='Requested') | Q(is_active=False))

        
        return queryset
        




class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all().prefetch_related('reviews')
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'slug'
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        return {'request' : self.request}

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.all().prefetch_related('reviews')


        if user.is_anonymous or not user.is_authenticated :
            queryset = queryset.filter(status='Approved', is_active=True)
        
        if user.is_staff:
            queryset = queryset.exclude(status='Pending')
        
        elif hasattr(user, 'role'):
            if user.role == 'tutor':
                queryset = queryset.all()
            elif user.role == 'student':
                queryset = queryset.filter( Q(status='Approved', is_active=True))
                # purchased_courses = Course.objects.filter(student_progress__student=user)
                # queryset = queryset.filter(
                #     Q(status='Approved', is_active=True) |
                #     Q(id__in=purchased_courses.values('id'))
                # ).distinct()
        
        category_query = self.request.query_params.get('category', None)
        if category_query:
            queryset = queryset.filter(category__slug=category_query)

        request_query = self.request.query_params.get('request_course', None)
        if request_query:
            queryset = queryset.filter(status='Requested')

        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset
        
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'tutor_profile'):
            serializer.save(tutor=self.request.user.tutor_profile)   


    def get_object(self):
        print(self.kwargs)
        slug = self.kwargs.get('slug', None)
        if slug:
            data = Course.objects.filter(slug=slug).first()
            print(data)
        return data


class ModuleView(APIView):
    def post(self, request, *args, **kwargs):
        print('requested data',request.data)
        modules_data = json.loads(request.data.get('modules'))
        print('module data ',modules_data)
        course_id = request.data.get('course')
        print('module daata', course_id)
        course = Course.objects.get(id=course_id)

        print(course)
        course.status = 'Requested'
        course.save()


        for i, data in enumerate(modules_data):
            # print(i, data)
            title = data['title']
            description = data['description']
            duration = data['duration']
            video = request.FILES.get(f'video_{i}')
            notes = request.FILES.get(f'notes_{i}')

            Module.objects.create(
                course=course,
                description=description,
                duration = duration,
                title=title,
                video=video,
                notes=notes
            )

        return Response(data={'message' : 'Modules create sucessfully'}, status=status.HTTP_201_CREATED)



class EditModuleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsTutor | IsStudent]

    

    def patch(self, request, *args, **kwargs):
        if 'toggle-like' in request.path:
            return self.toggle_like(request, *args, **kwargs)
        if 'mark-watched' in request.path:
            return self.mark_watched(request, *args, **kwargs)
        return super().patch(request, *args, **kwargs)

    def toggle_like(self, request, pk=None):
        module = get_object_or_404(Module, pk=pk)
        student = request.user

        course_progress, create = StudentCourseProgress.objects.get_or_create(student=student, course=module.course)

        if course_progress.liked_modules.filter(id=module.id).exists():
            course_progress.liked_modules.remove(module)
            module.likes_count = max(0, module.likes_count-1)

        else:
            course_progress.liked_modules.add(module)
            module.likes_count += 1
        
        module.save()
        course_progress.save()

        return Response({'likes_count' : module.likes_count, 'is_liked' : course_progress.liked_modules.filter(id=module.id).exists()}, status=status.HTTP_200_OK)
    
    def mark_watched(self, request, pk=None):
        module = get_object_or_404(Module, pk=pk)
        student = request.user
        module.views_count += 1

        course_progress, created = StudentCourseProgress.objects.get_or_create(
            student=student,
            course=module.course
        )

        if not course_progress.watched_modules.filter(id=module.id).exists():
            course_progress.watched_modules.add(module)
            course_progress.watch_time += module.duration
            course_progress.last_accessed_module = module
            course_progress.save()

        return Response({'message' : 'Marked watched module'}, status=status.HTTP_200_OK)







class CoursePurchaseView(APIView):
    def post(self, request, *args, **kwargs):
        
        print(request.data)
        print(request.user)
        user = request.user
        course_id = request.data.get('course_id', '')
        access_type = request.data.get('access_type', '')
        print(course_id, access_type)

        if not user.is_authenticated:
            return Response({'error' : 'Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            print(' not couse found', e)
            return Response({'error' : 'Course not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        price = course.price if access_type == 'Lifetime' else course.rental_price
        print('price of course to purchase ', price)

        # image_url = request.build_absolute_uri(course.thumbnail.url) 
        # print("Image URL ", image_url)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {   
                        'price_data' : {
                            'currency' : 'inr',
                            'product_data' : {
                                'name' : course.title,
                                'description' : course.description,
                                # 'images' : [image_url],
                            },
                            'unit_amount' : int(price * 100)
                            
                        },
                        'quantity' : 1

                    },
                ],
                mode='payment',
                success_url = f'{settings.SITE_URL}payment_success?course_id={course.slug}&user_id={user.id}&access_type={access_type}&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f"{settings.SITE_URL}payment_failed?course_id={course.slug}&user_id={user.id}",
            )

            
            print(checkout_session.url)
            print('session id' ,checkout_session.id)
            return Response({'session_id' : checkout_session.id, 'url' : checkout_session.url, })
        except Exception as e:
            print(e)
            return Response({
                'error' : 'Something went wrong when create stripe checkout session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class PaymentSuccess(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        access_type = data.get('access_type')
        session_id = data.get('session_id')

        if not course_id:
            return Response({'error' : 'course not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error' : 'user not found'}, status=status.HTTP_400_BAD_REQUEST)
        if not access_type:
            return Response({'error' : 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)
        if not session_id:
            return Response({'error' : 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)




        try:
            with transaction.atomic():
                course = Course.objects.get(slug=course_id)
                user_id = CustomUser.objects.get(id=user_id)


                existing_progress = StudentCourseProgress.objects.filter(student=user_id, course=course).first()
                if existing_progress:
                    if access_type == 'Rental' and existing_progress.access_expiry_date and existing_progress.access_expiry_date > datetime.now().date():
                        return Response({'message' : 'already has access to this course'}, status=status.HTTP_200_OK)
                    

                if access_type == 'Rental':
                    rental_duration_days = int(course.rental_duration)
                    access_expiry_date = datetime.now().date() + timedelta(days=rental_duration_days)
                    print(rental_duration_days, access_expiry_date)
                else:
                    access_expiry_date = None


                Transaction.objects.create(
                    user =user_id,
                    course = course,
                    amount = course.price if access_type == 'LifeTime' else course.rental_price ,
                    status='Completed',
                    reference_id = session_id,
                    access_type= access_type,
                    access_expiry_date = access_expiry_date
                )

                StudentCourseProgress.objects.create(
                    student = user_id,
                    course = course,
                    progress = 'Not Started',
                    access_type= access_type,
                    access_expiry_date = access_expiry_date
                )

                course.total_enrollment += 1
                course.save()
                print('coruse total enrollment increament')

            print('created')
            return Response({'message' : "payment success and access granted"}, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({'error' : 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error' : 'user not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error' : str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsStudent]


    def get_serializer_context(self):
        return {'request' : self.request}


    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({'error' : 'You are not authorized to edit thi review'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response({'error' : 'You are not authrized persron to edit'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class NotesViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NotesSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        print('requst user in notes :',self.request.user)
        return Note.objects.filter(user=self.request.user)


