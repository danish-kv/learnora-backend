Learnora Backend
Welcome to the Learnora Backend repository! Learnora is an innovative e-learning platform designed for students, tutors, and admins, providing an interactive, collaborative, and engaging learning experience.

Overview
Learnora is a comprehensive platform offering features such as course creation, community-based learning, contests, and more. It supports three main user roles:

Student: Can purchase or rent courses, take notes, participate in contests, and join discussions.
Tutor: Can create courses, manage communities, and participate in video chats and group discussions.
Admin: Oversees user management, course approval, and category management.
Key Features
Authentication: Google OAuth and JWT-based authentication for secure access.
Course Management: Tutors can create courses, and students can purchase or rent courses based on modules or chapters.
Note-taking and Review: Students can take notes during lessons and review them later.
Contest Section: A gamified contest system with MCQ questions created by tutors, designed for student engagement. Time-limited challenges are supported.
Discussion Forum: A public forum where students can ask questions, share achievements, and interact with upvotes, downvotes, comments, and nested replies.
Community Section: Group chat and video call features for live tutoring sessions and collaborative study, powered by ZegoCloud.
Chatbot: Integrated AI-powered chatbot using Gemini AI for resolving doubts.
Profile Management: Students can manage their profiles, track achievements, and monitor learning progress.
Admin Features
User Management: Admins can manage both students and tutors.
Course Approval: Admins review and approve courses created by tutors.
Category Management: Manage and categorize courses for better discovery.
Tutor Features
Course Management: Tutors can manage their courses and request new categories.
Community Management: Tutors can manage community groups for live discussions.
Profile Management: Tutors can manage and update their profiles.
Technologies Used
The Learnora backend is built with a modern tech stack to ensure performance, scalability, and security:

Django: Backend framework.
Django REST Framework (DRF): For building robust APIs.
Django Channels: Enables real-time communication features.
PostgreSQL: Relational database management system.
Redis: Used for caching.
Celery & Celery Beat: For handling background tasks, including contest scheduling and other periodic tasks.
Amazon S3: Used for media and static file storage.
JWT (JSON Web Token): For user authentication and authorization.
Google OAuth: Social authentication for user login.
ZegoCloud: For real-time video calls and group chat features.
Gemini AI: AI-powered chatbot for student assistance and doubt resolution.
Installation & Setup
To get started with the Learnora backend, follow these steps:

Prerequisites
Python 3.x
PostgreSQL
Redis
AWS S3 (for media and static files)
Django
Celery
Step 1: Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/learnora-backend.git
cd learnora-backend
Step 2: Create and Activate a Virtual Environment
bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
Step 3: Install Dependencies
bash
Copy code
pip install -r requirements.txt
Step 4: Configure Environment Variables
Set up your environment variables in a .env file, including:

Database credentials for PostgreSQL
Redis URL
AWS S3 credentials
Google OAuth credentials
JWT secret keys
Step 5: Run Migrations
bash
Copy code
python manage.py migrate
Step 6: Start Celery Worker and Beat
To manage scheduled tasks, such as contest scheduling, start the Celery worker and Celery beat:

bash
Copy code
celery -A learnora worker --loglevel=info
celery -A learnora beat --loglevel=info
Step 7: Run the Server
bash
Copy code
python manage.py runserver
Features Breakdown
Course Management
Tutors can create and manage courses.
Students can browse, purchase, rent, and watch courses.
Courses are organized by modules and chapters, offering a structured learning path.
Contests & Gamification
Tutors create MCQ-based contests.
Students participate in time-limited contests for gamified learning.
Discussion Forum
Students can ask questions, post achievements, and engage with the community through upvotes, downvotes, comments, and replies.
Community Section
Group chat and live video calls for enhanced tutor-student and student-student interaction.
APIs
Learnora provides a comprehensive set of APIs for all major functionalities, including:

User Authentication: Google OAuth, JWT token generation, and verification.
Course Management: CRUD operations for courses, chapters, and modules.
Community & Chat: Real-time chat and video calls.
Contests: Creating, joining, and managing contests.
Forum & Discussions: Post, comment, reply, upvote, and downvote features.
For detailed API documentation, refer to the /docs endpoint after running the project.

Contributing
We welcome contributions to Learnora! Please read our CONTRIBUTING.md file for guidelines on how to get involved.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For more information or inquiries, please contact:

Project Owner: Danish