import pyttsx3
import speech_recognition as sr


engine = pyttsx3.init()
engine.setProperty("rate", 170)

voices = engine.getProperty("voices")

voice_to_get_index = 0  # Default value

for voice_number in voices:
    if voice_number.id == 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0':
        voice_to_get_index = voices.index(voice_number)

engine.setProperty("voice", voices[voice_to_get_index].id)

r = sr.Recognizer()


def listen():
    with sr.Microphone() as source:
        print("Escuchando...")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio, language="es-ES")
            print("He entendido: {}".format(text))
            return text
        except sr.UnknownValueError:
            print("Lo siento, no te he entendido")
            return
            # returns None


def say(text):
    engine.say(text)
    engine.runAndWait()


def main():
    say("Esto es una prueba")
    listen()


if __name__ == "__main__":
    main()
