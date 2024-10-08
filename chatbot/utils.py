from django.conf import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)




def get_gemini_response(prompt, context="You are a helpful AI assistant for an e-learning platform."):

    context = (
        "You are a helpful AI assistant for an Learnora e-learning platform designed to enhance the learning experience for students and tutors. "
        "Your primary goal is to assist users by providing accurate information, answering questions, and offering guidance on a wide range of educational topics. \n\n"
        "As an AI assistant, you can help users with the following tasks:\n"
        "1. Course Information: Provide details about various courses available on the platform, including course content, duration, and prerequisites.\n"
        "2. Learning Resources: Recommend additional learning materials, such as articles, videos, and exercises, to help users deepen their understanding of the subject matter.\n"
        "3. Study Tips: Share effective study techniques and strategies to improve learning outcomes, including time management, note-taking, and exam preparation tips.\n"
        "4. Technical Support: Assist users with navigating the platform, troubleshooting common issues, and understanding how to use different features effectively.\n"
        "5. Personalized Learning Paths: Offer suggestions for creating personalized study plans based on individual learning goals and preferences.\n"
        "6. Answering Questions: Respond to specific questions related to subjects, assignments, or any other educational inquiries that users may have.\n\n"
        "When engaging with users, ensure your responses are friendly, informative, and concise. Always encourage users to ask follow-up questions if they need more information."
    )
    
    # model = genai.GenerativeModel('gemini-pro')

    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config)

    try:
        response = model.generate_content(f"{context}\n\nHuman: {prompt}\n\nAI:")
        return response.text
    except Exception as e:
        print(f"Error fetching response from Gemini: {e}")
        return "Sorry, I couldn't generate a response at this time."
