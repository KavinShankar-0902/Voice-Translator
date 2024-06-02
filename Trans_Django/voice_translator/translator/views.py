import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import pygame
import time
import json

# Render the index.html template
def index(request):
    return render(request, 'translator/index.html')

# View to handle processing of audio input
@csrf_exempt
# View to handle processing of audio input
@csrf_exempt
def process_audio(request):
    if request.method == 'POST':
        try:
            # Extract language code and target languages from request
            data = json.loads(request.body.decode('utf-8'))
            # Get language code from request POST data or default to 'ta-IN'
            language_code = data.get('language_code', 'en-US')
            target_languages = data.get('target_languages', [])  # Get a list of target languages from request data

            # Recognize speech from the input voice
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                audio_data = recognizer.listen(source)
                # Specify the language parameter for recognition
                input_voice = recognizer.recognize_google(audio_data, language=language_code)

            # Translate the recognized text to the target languages
            translator = Translator()
            translated_texts = {}
            for target_language in target_languages:
                translated_text = translator.translate(input_voice, dest=target_language).text
                translated_texts[target_language] = translated_text

            # Convert translated texts to speech in the respective target languages
            for target_language, translated_text in translated_texts.items():
                output_file = f"translated_speech_{target_language}.mp3"
                tts = gTTS(translated_text, lang=target_language)
                # Check if the file exists and remove it if it does
                if os.path.exists(output_file):
                    os.remove(output_file)
                tts.save(output_file)
                # Play the translated speech
                play_audio(output_file)

            return JsonResponse({'recognized_text': input_voice, 'translated_texts': translated_texts})

        except sr.UnknownValueError:
            return JsonResponse({'error': 'Unable to recognize speech'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


# Function to play audio file
def play_audio(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
        time.sleep(1)
    pygame.mixer.music.unload()
    pygame.mixer.quit()
