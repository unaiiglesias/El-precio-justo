import pyttsx3
import speech_recognition as sr


engine = pyttsx3.init()
engine.setProperty("rate", 170)
engine.setProperty("voice", "spanish")
# IDK why but sometimes that doesn't work, so:
try:
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
except Exception:
    pass
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
