import pyttsx3
import speech_recognition as sr
import wikipedia
from fuzzywuzzy import fuzz

class Chatbot:
    def __init__(self):
        self.engine = pyttsx3.init("sapi5")
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voices', voices[1].id)
        self.engine.setProperty('rate', 150)
        self.recognizer = sr.Recognizer()

    def speak(self, audio):
        self.engine.say(audio)
        print(audio)
        self.engine.runAndWait()

    def take_command(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.pause_threshold = 3
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, timeout=10)
            try:
                print("Recognizing...")
                query = self.recognizer.recognize_google(audio, language='en-in')
                print(f'You said: {query}\n')
                return query
            except Exception as e:
                print("Say that again please")
                return "None"

    def clean_summary(self, summary):
        cleaned_summary = summary.replace('== Content ==', '')
        return cleaned_summary

    def search_answers(self, question):
        try:
            with open('questions.txt', 'r') as q_file, open('answers.txt', 'r') as a_file:
                questions = q_file.readlines()
                answers = a_file.readlines()
                highest_match = -1
                best_answer = None
                for i, q in enumerate(questions):
                    similarity = fuzz.ratio(question.strip().lower(), q.strip().lower())
                    if similarity > highest_match:
                        highest_match = similarity
                        best_answer = answers[i].strip()

                if highest_match >= 75:
                    return best_answer

            return None
        except FileNotFoundError:
            return None

    def chatbot_response(self, user_input):
        response = ""

        if "text" in user_input:
            response = "You are now in text mode. How can I assist you?"
            while True:
                question = input("You: ").lower()
                if question == "exit":
                    response = "Goodbye!"
                    break
                elif question == "help":
                    response = "You can ask me questions or give me commands."
                else:
                    answer = self.search_answers(question)
                    if answer:
                        response = answer
                    else:
                        try:
                            result = wikipedia.summary(question, sentences=2)
                            cleaned_result = self.clean_summary(result)
                            response = f"{cleaned_result}\n\nWikipedia Link: {wikipedia.page(question).url}"
                        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                            response = "I couldn't find an answer. Can you please rephrase your question?"
                print("Chatbot:", response)

        elif "voice" in user_input:
            response = "You are now in voice mode. How can I assist you?"
            self.speak(response)
            while True:
                voice_input = self.take_command().lower()
                if "exit" in voice_input:
                    response = "Goodbye!"
                    break
                answer = self.search_answers(voice_input)
                if answer:
                    self.speak("Chatbot: " + answer)
                else:
                    try:
                        result = wikipedia.summary(voice_input, sentences=2)
                        cleaned_result = self.clean_summary(result)
                        self.speak("Chatbot: " + cleaned_result)
                        print("Wikipedia Link:", wikipedia.page(voice_input).url)
                    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
                        response = "I couldn't find an answer. Can you please rephrase your question?"
                print("Next question")

        return response

def main():
    chatbot = Chatbot()
    chatbot.speak("Hello. My name is AURA. Please type text or voice mode to proceed.")
    
    while True:
        user_input = input("You: ").lower()

        if "exit" in user_input:
            break

        response = chatbot.chatbot_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    main()