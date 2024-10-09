from django.conf import settings
import google.generativeai as genai

# Configure the Gemini API with the provided API key from settings
genai.configure(api_key=settings.GEMINI_API_KEY)


def get_gemini_response(prompt, context="You are a helpful AI assistant for an e-learning platform."):
    """
    Generate a response from the Gemini AI based on the provided prompt.

    Args:
        prompt (str): The user's input message or question.
        context (str): The context in which the AI should operate (default is a generic assistant).

    Returns:
        str: The AI's generated response or an error message if unable to generate.
    """

    # Define the specific context for the AI assistant
    context = (
        "You are a helpful AI assistant for the Learnora e-learning platform designed to enhance the learning experience for students and tutors. "
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

    # Configuration for the generation model

    """
    temperature: Adjusts the creativity and randomness of the output.
    top_p: Determines the diversity of responses by focusing on the cumulative probability of word choices.
    top_k: Restricts the word selection to the most probable candidates.
    max_output_tokens: Sets the limit on the length of the generated output.
    response_mime_type: Defines the format of the output response.
    """

    generation_config = {
        "temperature": 1,                  
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1000,
        "response_mime_type": "text/plain",
    }

    # Initialize the model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config
    )

    try:
        # Generate content using the model
        response = model.generate_content(f"{context}\n\nHuman: {prompt}\n\nAI:")
        return response.text
    except Exception as e:
        # Handle any errors that occur during response generation
        return "Sorry, I couldn't generate a response at this time."


