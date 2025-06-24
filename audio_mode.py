# audio_mode.py
import speech_recognition as sr
import wikipedia
from googlesearch import search
import pyttsx3
import requests
from bs4 import BeautifulSoup

# Initialize TTS engine
tts_engine = pyttsx3.init()

def speak(text: str):
    """Speaks the given text aloud."""
    tts_engine.say(text)
    tts_engine.runAndWait()

def transcribe_speech(timeout=5, phrase_time_limit=10) -> str:
    """Convert speech to text using the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand your speech."
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"

def search_google(query: str) -> str:
    """Get the first snippet from a Google search result."""
    try:
        for result in search(query, num_results=1):
            page = requests.get(result, timeout=10)
            soup = BeautifulSoup(page.text, "html.parser")
            p_tags = soup.find_all('p')
            if p_tags:
                return p_tags[0].get_text().strip() + f"\n\nSource: {result}"
    except Exception as e:
        return f"Error fetching from Google: {e}"
    return "No result found."

def get_answer_from_wikipedia(query: str) -> str:
    """Get a brief summary from Wikipedia."""
    try:
        summary = wikipedia.summary(query, sentences=2)
        return f"{summary}\n\nSource: https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Your query was too broad. Try to be more specific."
    except wikipedia.exceptions.PageError:
        return "No Wikipedia page found."
    except Exception as e:
        return f"Error fetching from Wikipedia: {e}"

def transcribe_and_answer() -> str:
    """Listen for a question, search Wikipedia & Google, return the best answer."""
    question = transcribe_speech()
    if question.startswith("Error") or question.startswith("Sorry"):
        return question

    wiki_answer = get_answer_from_wikipedia(question)
    if wiki_answer.startswith("Error") or wiki_answer.startswith("No"):
        # If Wikipedia fails, fall back to Google
        answer = search_google(question)
    else:
        answer = wiki_answer

    # Speak the answer aloud
    speak(answer)
    return answer