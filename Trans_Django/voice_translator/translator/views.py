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

def index(request):
    return render(request, 'translator/index.html')

@csrf_exempt
@csrf_exempt
def process_audio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            language_code = data.get('language_code', 'en-US')
            target_languages = data.get('target_languages', [])  

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                audio_data = recognizer.listen(source)
                input_voice = recognizer.recognize_google(audio_data, language=language_code)

            translator = Translator()
            translated_texts = {}
            for target_language in target_languages:
                translated_text = translator.translate(input_voice, dest=target_language).text
                translated_texts[target_language] = translated_text

            for target_language, translated_text in translated_texts.items():
                output_file = f"translated_speech_{target_language}.mp3"
                tts = gTTS(translated_text, lang=target_language)
                if os.path.exists(output_file):
                    os.remove(output_file)
                tts.save(output_file)
                play_audio(output_file)

            return JsonResponse({'recognized_text': input_voice, 'translated_texts': translated_texts})

        except sr.UnknownValueError:
            return JsonResponse({'error': 'Unable to recognize speech'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def play_audio(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): 
        time.sleep(1)
    pygame.mixer.music.unload()
    pygame.mixer.quit()
