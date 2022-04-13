import os
import random
import re
from io import BytesIO
import PIL
from speak_and_listen import say, listen
import requests_html
from PIL import Image
# Quita el error por no verificar el certificado, linea 59 (funcion mostrar imagen)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables
P1_Wins = 0
P2_Wins = 0
rounds_played = 0


def get_categories(session):
    site_home = session.get("https://www.coolmod.com/")
    return site_home.html.find(".subfamilyheadertittle")


def get_random_category_link(all_categories):
    category = random.choice(all_categories)

    while category.text == "Configura tu PC a Medida":
        category = random.choice(all_categories)
        # Ha tocado el configurador
    return list(category.links)[0]


def proccess_products(session, category_link):
    product_category_page = session.get(category_link)
    products = product_category_page.html.find(".productInfo")

    product = random.choice(products)

    # Get product name
    product_name = product.text.split("\n")[1]

    # Get product price
    product_price = product.text.split("\n")[-1]
    product_price = float(product_price.replace("€", "").replace(" ", "").replace(".", "").replace(",", "."))
    # Quitar el sinbolo € y los espacios. Arreglar el numero para convertirlo en float

    # Get product image
    img_src = product.html.split("\n")[5]
    product_image_link = re.findall("(https://[A-aZ-z./-9-0]+)", img_src)[0]

    return product_name, product_price, product_image_link


def listen_and_get_user_guess():
    user_guess = listen()
    try:
        user_guess = user_guess.replace(" €", "").replace("euros", "")\
            .replace(",", ".").replace(" con ", ".").replace(" coma ", ".")
        final_user_guess = float(user_guess)
        return final_user_guess
    except ValueError:
        say("Lo siento, no te he entendido. ¿Te importaría repetirlo?")
        return listen_and_get_user_guess()
    except AttributeError:
        say("Lo siento, no te he entendido. ¿Te importaría repetirlo?")
        return listen_and_get_user_guess()


def show_product_image(product_image_link, session):
    try:
        product_image_downloaded = session.get(product_image_link, verify=False)
        image = Image.open(BytesIO(product_image_downloaded.content))
        image.show()
    except PIL.UnidentifiedImageError:
        print("No se ha podido mostrar la imagen")
    pass


def ask_and_check_user_guess(product_name, product_image_link, session):
    print("Nombre del producto {}".format(product_name))
    show_product_image(product_image_link, session)
    say("El nombre del producto es {}".format(product_name))

    say("¿Cuanto vale? Jugador 1")
    P1_guess = listen_and_get_user_guess()

    say("¿Cuanto vale? Jugador 2")
    P2_guess = listen_and_get_user_guess()

    return P1_guess, P2_guess


def set_round_number():
    print("Cuantas rondas te gustaría jugar?")
    say("Cuantas rondas te gustaría jugar?")
    numbers_in_words = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]

    user_input = listen()
    if user_input in numbers_in_words:
        user_input = numbers_in_words.index(user_input)
    elif user_input == "una":
        user_input = 1

    try:
        number_of_rounds = int(user_input)
        print(number_of_rounds)
        return number_of_rounds
    except ValueError:
        say("Lo siento, no te he entendido")
        return set_round_number()
    except AttributeError:
        say("Lo siento, no te he entendido")
        return set_round_number()
    except TypeError:
        say("Lo siento, no te he entendido")
        return set_round_number()


def determine_winner(P1_guess, P2_guess, product_price):
    global P1_Wins
    global P2_Wins
    global rounds_played

    P1_absolute_error = round(abs(P1_guess - product_price), 2)
    P2_absolute_error = round(abs(P2_guess - product_price), 2)

    if P1_absolute_error < P2_absolute_error:
        P1_Wins += 1
        say("El primer jugador se ha acercado a {} euros.".format(P1_absolute_error))
    elif P1_absolute_error > P2_absolute_error:
        P2_Wins += 1
        say("El segundo jugador se ha acercado a {} euros.".format(P2_absolute_error))
    else:  # If both errors are the same
        if random.randint(1,2) == 1:
            P1_Wins += 1
        else:
            P2_Wins += 1
    rounds_played += 1
    return


def print_title():
    title = "EL PRECIO JUSTO by Unai Iglesias"
    print("+" + "-" * len(title) + "+")
    print("|" + title + "|")
    print("+" + "-" * len(title) + "+")
    return


def print_winner(winner):
    content = "Ha ganado el " + winner + " ¡Felicidades!"
    print("+" + "-" * len(content) + "+")
    print("|" + content + "|")
    print("+" + "-" * len(content) + "+")
    return


def main():
    # Initialization
    global P1_Wins
    global P2_Wins
    global rounds_played
    os.system("cls")
    session = requests_html.HTMLSession()
    winner = None
    print_title()
    say("Bienvenidos a El precio justo, vamos a adivinar el precio de algunos productos")

    all_categories = get_categories(session)

    number_of_rounds = set_round_number()

    # End of initialization

    # Main game loop
    while (P1_Wins < number_of_rounds) and (P2_Wins < number_of_rounds):
        os.system("cls")
        category_link = get_random_category_link(all_categories)
        product_name, product_price, product_image_link = proccess_products(session, category_link)

        # Ask for guesses
        P1_guess, P2_guess = ask_and_check_user_guess(product_name, product_image_link, session)

        # Reveal real product price
        product_price_adapted_to_speech = str(round(product_price, 2)).replace(".", "coma")
        say("El precio era {} euros".format(product_price_adapted_to_speech))
        print("El precio era {} €.".format(round(product_price, 2)))

        determine_winner(P1_guess, P2_guess, product_price)

        if P1_Wins == number_of_rounds:
            winner = "primer jugador"
            os.system("cls")
        elif P2_Wins == number_of_rounds:
            winner = "segundo jugador"
            os.system("cls")
        else:
            say("Siguiente ronda.")

    print_winner(winner)

    say("Ha ganado el {}. ¡Felicidades!".format(winner))
    os.system("pause")

if __name__ == "__main__":
    main()


"""
- 5 rondas
- Hacer que el juego sea de dos jugadores
- Dejar al usuario escoger categoria (Diccionario)
- Arreglar sistema de rondas
"""