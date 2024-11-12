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
from django.shortcuts import get_object_or_404
from datetime import datetime
from datetime import timedelta
from django.db import transaction
import json
import stripe
from base.custom_pagination_class import CustomPagination
from base.custom_permissions import IsAdmin, IsStudent, IsTutor
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.core.cache import cache
from rest_framework.exceptions import NotFound
import boto3
from rest_framework.decorators import api_view

# Set the Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY





@api_view(['GET'])
def get_presigned_url(request):
    
    s3 = boto3.client('s3',
                     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    
    file_type = request.GET.get('file_type') 
    filename = request.GET.get('filename')
    

    if file_type == 'video':
        key = f'module_videos/{filename}'  
    elif file_type == 'notes':
        key = f'module_notes/{filename}' 
    else:
        return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    presigned_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=3600  
    )
    
    return Response({'presignedUrl': presigned_url, 'key': key})



class CategoryViewSet(ModelViewSet):
    """
    API view for handling Category operations.
    Provides list, create, update, and delete functionalities for categories.
    """

    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Override get_queryset to filter categories based on user role and cache results.
        """
        user = self.request.user
        cache_key = f'categories_{user.id if user.is_authenticated else "public"}'
        cached_category = cache.get(cache_key)

        if cached_category is not None:
            return cached_category

        queryset = Category.objects.all().order_by('id')

        # Filter categories based on user authentication and role
        if user.is_anonymous:
            queryset = queryset.filter(Q(status='Approved') & Q(is_active=True))

        if user.is_staff:
            queryset = queryset.exclude(status='Requested')
        elif hasattr(user, 'role'):
            if user.role == 'student':
                queryset = queryset.filter(Q(status='Approved') & Q(is_active=True))
            elif user.role == 'tutor':
                queryset = queryset.exclude(Q(status='Requested') | Q(is_active=False))

        # Cache the filtered queryset
        cache.set(cache_key, queryset, 60 * 15)
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new category and invalidate cache.
        """
        response = super().create(request, *args, **kwargs)
        self.invalidate_all_cache()
        return response

    def update(self, request, *args, **kwargs):
        """
        Update an existing category and invalidate cache.
        """
        response = super().update(request, *args, **kwargs)
        self.invalidate_all_cache()
        return response

    def destroy(self, request, *args, **kwargs):
        """
        Delete a category and invalidate cache.
        """
        response = super().destroy(request, *args, **kwargs)
        self.invalidate_all_cache()
        return response

    def invalidate_all_cache(self):
        """
        Invalidate all cached data.
        """
        cache.clear()




class CourseViewSet(ModelViewSet):
    """
    API view for handling Course operations.
    Provides list, create, update, and delete functionalities for courses.
    """

    queryset = Course.objects.all().prefetch_related('reviews')
    serializer_class = CourseSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'slug'
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        """
        Override get_serializer_context to add the request to the context.
        """
        return {'request': self.request}

    def get_queryset(self):
        """
        Override get_queryset to filter courses based on user role and cache results.
        """
        user = self.request.user
        category = self.request.query_params.get('category', '')
        cache_key = f'courses_{user.id if user.is_authenticated else "public"}_{category}'
        cached_courses = cache.get(cache_key)

        if cached_courses is not None:
            return cached_courses

        queryset = Course.objects.all()\
                .select_related('tutor', 'category')\
                .prefetch_related('reviews')

        # Filter courses based on user authentication and role
        if user.is_anonymous:
            queryset = queryset.filter(status='Approved', is_active=True)
        elif user.is_staff:
            queryset = queryset.exclude(status='Pending')
        elif hasattr(user, 'role'):
            if user.role == 'tutor':
                queryset = queryset.filter(tutor__user=user)
            elif user.role == 'student':
                queryset = queryset.filter(Q(status='Approved', is_active=True, tutor__user__is_active=True, category__is_active=True))

        # Filter by category if provided
        if category:
            queryset = queryset.filter(category__slug=category)

        # Filter by request_course query parameter
        request_query = self.request.query_params.get('request_course', None)
        if request_query:
            queryset = queryset.filter(status='Requested')

        # Search functionality
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        # Cache the filtered queryset
        cache.set(cache_key, queryset, 60 * 15)

        return queryset

    def perform_create(self, serializer):
        """
        Override perform_create to save the course with the tutor profile.
        """
        if hasattr(self.request.user, 'tutor_profile'):
            serializer.save(tutor=self.request.user.tutor_profile)
        self.invalidate_all_cache()

    def perform_update(self, serializer):
        """
        Override perform_update to save changes to the course and invalidate cache.
        """
        serializer.save()
        self.invalidate_all_cache()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to delete the course and invalidate cache.
        """
        instance.delete()
        self.invalidate_all_cache()

    def invalidate_all_cache(self):
        """
        Invalidate all cached data.
        """
        cache.clear()

    def get_object(self):
        """
        Override get_object to retrieve a course by its slug.
        """
        user = self.request.user
        slug = self.kwargs.get('slug', None)

        if slug:
            if hasattr(user, 'role') and (user.role == 'tutor' or user.role == 'admin'):
                # Admin or tutor can retrieve any course
                course = Course.objects.filter(slug=slug).first()
            else:
                # Other users can only retrieve active courses with active categories
                course = Course.objects.filter(slug=slug, is_active=True, category__is_active=True).first()

            if course:
                return course
            else:
                raise NotFound(detail="Course not found")

        # If slug is not provided
        raise NotFound(detail="Course not found")



# Define the view to handle module creation
class ModuleView(APIView):
    """
    API view to handle module creation for a specific course.
    """

    def post(self, request, *args, **kwargs):
        """
        Create modules for the specified course.
        """
        modules_data = json.loads(request.data.get('modules'))
        course_id = request.data.get('course')

        # Retrieve the course and update its status
        course = Course.objects.get(id=course_id)
        course.status = 'Requested'
        course.save()

        # Create modules based on the provided data
        for i, data in enumerate(modules_data):
            title = data['title']
            description = data['description']
            duration = data['duration']
            video = data.get('video') 
            notes = data.get('notes') 

            Module.objects.create(
                course=course,
                description=description,
                duration = duration,
                title=title,
                video=video,
                notes=notes
            )

        return Response(data={'message' : 'Modules create sucessfully'}, status=status.HTTP_201_CREATED)


# Define the view to edit, retrieve, and delete modules
class EditModuleView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to handle retrieval, updating, and deletion of modules.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsTutor | IsStudent]

    def patch(self, request, *args, **kwargs):
        """
        Handle patch requests for toggling likes or marking a module as watched.
        """
        try:
            if 'toggle-like' in request.path:
                return self.toggle_like(request, *args, **kwargs)
            if 'mark-watched' in request.path:
                return self.mark_watched(request, *args, **kwargs)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return super().patch(request, *args, **kwargs)

    def perform_update(self, serializer):
        """
        Handle the manual update of the 'video' and 'notes' paths.
        """
        instance = self.get_object()

        # Handle video and notes path updates manually
        video_url = self.request.data.get('video', '')
        notes_url = self.request.data.get('notes', '')

        # Manually update video and notes
        if video_url:
            instance.video = video_url
        if notes_url:
            instance.notes = notes_url


        # Now let the serializer handle the rest of the fields
        validated_data = serializer.validated_data
        validated_data.pop('video', None)  
        validated_data.pop('notes', None)  

        # Update remaining fields with serializer and save
        for key, value in validated_data.items():
            setattr(instance, key, value)

        # Save the instance
        instance.save()

        # manually update the video and notes fields
        if video_url:
            instance.video = video_url
        if notes_url:
            instance.notes = notes_url

        instance.save()  # Save again to persist video and notes



    def toggle_like(self, request, pk=None):
        """
        Toggle the like status of a module for the authenticated user.
        """
        module = get_object_or_404(Module, pk=pk)
        student = request.user

        course_progress, _ = StudentCourseProgress.objects.get_or_create(student=student, course=module.course)

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
        """
        Mark a module as watched for the authenticated user.
        """
        module = get_object_or_404(Module, pk=pk)
        student = request.user
        module.views_count += 1
        module.save()

        course_progress, _ = StudentCourseProgress.objects.get_or_create(student=student, course=module.course)
        course_progress.progress = "Ongoing"

        if not course_progress.watched_modules.filter(id=module.id).exists():
            course_progress.watched_modules.add(module)
            course_progress.watch_time += module.duration
            course_progress.last_accessed_module = module
        
        total_modules = module.course.modules.count()
        watched_modules_count = course_progress.watched_modules.count()

        if total_modules == watched_modules_count:
            course_progress.progress = 'Completed'
        
        course_progress.save()

        return Response({'message': 'Marked watched module'}, status=status.HTTP_200_OK)


# Define the view for handling course purchases
class CoursePurchaseView(APIView):
    """
    API view to handle course purchases by users.
    """

    def post(self, request, *args, **kwargs):
        """
        Create a Stripe checkout session for course purchase.
        """
        user = request.user
        course_id = request.data.get('course_id', '')
        access_type = request.data.get('access_type', '')

        if not user.is_authenticated:
            return Response({'error' : 'Please login'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response({'error' : 'Course not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        price = course.price if access_type == 'Lifetime' else course.rental_price

        image_url = request.build_absolute_uri(course.thumbnail.url) 

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {   
                        'price_data' : {
                            'currency' : 'inr',
                            'product_data' : {
                                'name' : course.title,
                                'description' : course.description,
                                'images' : [image_url],
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

            return Response({'session_id' : checkout_session.id, 'url' : checkout_session.url, })
        except Exception as e:
            return Response({
                'error' : 'Something went wrong when create stripe checkout session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Define the view for handling successful payments
class PaymentSuccess(APIView):
    """
    API view to handle successful payments and grant course access.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle successful payment notifications and update course access for the user.
        """
        data = request.data
        course_id = data.get('course_id')
        user_id = data.get('user_id')
        access_type = data.get('access_type')
        session_id = data.get('session_id')

        if not course_id or not user_id or not access_type or not session_id:
            return Response({'error': 'Incomplete payment information'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                course = Course.objects.get(slug=course_id)
                user = CustomUser.objects.get(id=user_id)

                existing_progress = StudentCourseProgress.objects.filter(student=user, course=course).first()
                if existing_progress and access_type == 'Rental' and existing_progress.access_expiry_date and existing_progress.access_expiry_date > datetime.now().date():
                    return Response({'message': 'User already has access to this course'}, status=status.HTTP_200_OK)
                    

                # Set access expiry date based on rental duration
                access_expiry_date = None
                if access_type == 'Rental':
                    rental_duration_days = int(course.rental_duration)
                    access_expiry_date = datetime.now().date() + timedelta(days=rental_duration_days)

                 # Create transaction record
                Transaction.objects.create(
                    user=user,
                    course=course,
                    amount=course.price if access_type == 'Lifetime' else course.rental_price,
                    status='Completed',
                    reference_id=session_id,
                    access_type=access_type,
                    access_expiry_date=access_expiry_date
                )

                # Create student course progress record
                StudentCourseProgress.objects.create(
                    student=user,
                    course=course,
                    progress='Not Started',
                    access_type=access_type,
                    access_expiry_date=access_expiry_date
                )

                course.total_enrollment += 1
                course.save()

            return Response({'message': "Payment successful and access granted"}, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        

# Define the viewset for managing reviews
class ReviewViewSet(ModelViewSet):
    """
    ViewSet to manage reviews for courses.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsStudent]

    def get_serializer_context(self):
        """
        Provide additional context to the serializer.
        """
        return {'request': self.request}

    def update(self, request, *args, **kwargs):
        """
        Override update method to check ownership of the review.
        """
        review = self.get_object()
        if review.user != request.user:
            return Response({'error': 'You are not authorized to edit this review'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to check ownership of the review.
        """
        review = self.get_object()
        if review.user != request.user:
            return Response({'error': 'You are not authorized to delete this review'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# Define the view for managing notes
class NotesViewSet(ModelViewSet):
    """
    API view to manage notes for a specific course.
    """

    queryset = Note.objects.all()
    serializer_class = NotesSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        """
        Override get_queryset to filter notes based on the user's role and cache results.
        """
        user = self.request.user
        cache_key = f'notes_{user.id}'
        cached_notes = cache.get(cache_key)


        print('hhhh')
        if cached_notes is not None:
            return cached_notes
        print('hhhh===========')
        
        # Filter notes by the authenticated user
        queryset = Note.objects.filter(user=user)

        # Cache the filtered queryset for 15 minutes
        cache.set(cache_key, list(queryset), 60 * 15)  
        return queryset
    
    def get_object(self):
        print('===========================')
        return super().get_object()
    
    def perform_create(self, serializer):
        """
        Override perform_create to save the note with the authenticated user and invalidate cache.
        """
        serializer.save(user=self.request.user)
        self.invalidate_all_cache() 

    def perform_update(self, serializer):
        """
        Override perform_update to save the note and invalidate cache.
        """
        serializer.save()
        self.invalidate_all_cache()

    def perform_destroy(self, instance):
        """
        Override perform_destroy to delete the note and invalidate cache.
        """
        print('heyy=====================')
        instance.delete()
        self.invalidate_all_cache()

    def invalidate_all_cache(self):
        """
        Invalidate all cached data.
        """
        cache.clear()

    def get_serializer_context(self):
        """
        Override get_serializer_context to provide the request context to the serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
