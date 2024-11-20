# Learnora Backend

Welcome to the Learnora Backend repository! Learnora is an innovative e-learning platform designed for students, tutors, and admins, providing an interactive, collaborative, and engaging learning experience.

## Overview

Learnora is a comprehensive platform offering features such as course creation, community-based learning, contests, and more. It supports three main user roles:

- **Student**: Can purchase or rent courses, take notes, participate in contests, and join discussions.
- **Tutor**: Can create courses, manage communities, and participate in video chats and group discussions.
- **Admin**: Oversees user management, course approval, and category management.

## Key Features

### Authentication
- Google OAuth integration
- JWT-based authentication for secure access

### Course Management
- Tutors can create and manage courses
- Students can purchase or rent courses based on modules/chapters
- Structured learning paths with module-based organization

### Learning Tools
- Note-taking system during lessons
- Review system for course content
- Contest section with MCQ-based challenges
- Time-limited contests for gamified learning

### Community Features
- Public discussion forum with Q&A
- Achievement sharing
- Upvotes, downvotes, comments, and nested replies
- Group chat and video calls powered by ZegoCloud
- AI-powered chatbot using Gemini AI for doubt resolution

### User Management
- Profile management for students and tutors
- Progress tracking and achievement monitoring
- Admin controls for user oversight

### Payment Integration

 - Secure payment processing with Stripe
 - Course purchase and rental options


## Technologies Used

- **Backend Framework**: Django
- **API Framework**: Django REST Framework (DRF)
- **Real-time Communication**: Django Channels
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Management**: Celery & Celery Beat
- **Storage**: Amazon S3
- **Authentication**: JWT & Google OAuth
- **Payment Integration**: STRIPE
- **Video Chat**: ZegoCloud
- **AI Integration**: Gemini AI
- **Containerization**: Docker & Docker Compose

## Installation & Setup

### Using Docker (Recommended)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/danish-kv/learnora-backend
   cd learnora-backend
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your configuration:
   ```env

   # Database
   DB_NAME=learnora_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=db
   DB_PORT=5432

   # Redis
   REDIS_URL=redis://redis:6379/0

   # AWS
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=your_email@gmail.com

   # AWS
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name

   # Google OAuth
   GOOGLE_OAUTH_CLIENT_ID=your_client_id
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret

   STRIPE_SECRET=your_stripe_secret
   # Gemini AI
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. **Build and Run with Docker Compose**
   ```bash
   # Build the images
   docker-compose build

   # Start the services
   docker-compose up -d

   # Run migrations
   docker-compose exec web python manage.py migrate

   # Create superuser (optional)
   docker-compose exec web python manage.py createsuperuser
   ```


### Manual Setup (Alternative)

1. **Prerequisites**
   - Python 3.x
   - PostgreSQL
   - Redis
   - AWS S3 account
   - Django
   - Celery

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Follow the same environment variable setup as in the Docker section.

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Celery Worker and Beat**
   ```bash
   celery -A learnora worker --loglevel=info
   celery -A learnora beat --loglevel=info
   ```

7. **Run the Server**
   ```bash
   python manage.py runserver
   ```

## Docker Configuration

The project includes several Docker containers:

- **web**: Django application
- **db**: PostgreSQL database
- **redis**: Redis cache
- **celery**: Celery worker
- **celery-beat**: Celery beat scheduler

### Docker Commands

```bash
# Build the images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Execute commands in containers
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec db psql -U postgres
```


## Features Breakdown

### Course Management
- Course creation and management for tutors
- Browse, purchase, and rental options for students
- Module and chapter-based course organization

### Contests & Gamification
- MCQ-based contest creation
- Time-limited challenges
- Student participation tracking

### Discussion Forum
- Question posting
- Achievement sharing
- Community engagement through voting system
- Nested comments and replies

### Community Section
- Real-time group chat
- Live video calls
- Interactive tutoring sessions

