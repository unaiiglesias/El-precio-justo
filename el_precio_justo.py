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
p1_Wins = 0
p2_Wins = 0
rounds_played = 0


def get_categories(session):
    site_home = session.get("https://www.coolmod.com/")
    return site_home.html.find(".subfamilyheadertittle")


def let_user_choose_category():
    category_dict = {"coolpc": 'https://www.coolmod.com/pcs-coolmod/',
                     "portátiles": 'https://www.coolmod.com/pcs-tablets-portatiles-portatiles/',
                     "PCs sobremesa": 'https://www.coolmod.com/pcs-tablets-portatiles-pcs-sobremesa/',
                     "componentes PC": 'https://www.coolmod.com/componentes-hardware-componentes-pc/'}

    say("Para esta primera ronda, puedes elegir categoría.")

    keys = []
    values = []
    for key, value in category_dict.items():
        keys.append(key)
        values.append(value)

    chosen_category_link = None
    while not chosen_category_link:
        os.system("cls")
        print("Categorías a elegir:\n" + ("\n".join(keys)) + "\n")  # Pendiente de arreglar
        user_input = listen()

        if user_input in keys:
            chosen_category = keys[keys.index(user_input)]
            say("Has elegido la categoría " + chosen_category)
            chosen_category_link = category_dict[chosen_category]
            os.system("cls")
            return chosen_category_link
        else:
            say("Lo siento, no te he entendido, repite tu elección por favor.")


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
    p1_guess = listen_and_get_user_guess()

    say("¿Cuanto vale? Jugador 2")
    p2_guess = listen_and_get_user_guess()

    return p1_guess, p2_guess


def set_round_number():
    print("Cuantas rondas te gustaría jugar? Debe de ser un numero impar.")
    say("Cuantas rondas te gustaría jugar? Debe de ser un numero impar")
    numbers_in_words = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]

    user_input = listen()
    try:
        user_input = user_input.split(" ")[0]  # In case input ~= 5 rondas
    except AttributeError:
        say("Lo siento, no te he entendido")
        return set_round_number()

    if user_input in numbers_in_words:
        user_input = numbers_in_words.index(user_input)
    elif user_input == "una":
        user_input = 1

    try:
        number_of_rounds = int(user_input)
    except (ValueError, AttributeError, TypeError):
        say("Lo siento, no te he entendido")
        return set_round_number()

    if (number_of_rounds % 2) == 0:  # El numero es par
        say(str(number_of_rounds) + " no es un numero impar")
        return set_round_number()

    print("La partida durará {} rondas.".format(number_of_rounds))
    say("La partida durará {} rondas.".format(number_of_rounds))
    return number_of_rounds


def pick_random_winner():
    global p1_Wins
    global p2_Wins

    if random.randint(1, 2) == 1:
        p1_Wins += 1
        print_round_winner("jugador 1")
        say("La ronda la gana el jugador 1.")
    else:
        p2_Wins += 1
        print_round_winner("jugador 2")
        say("La ronda la gana el jugador 2.")
    return


def determine_winner(p1_guess, p2_guess, product_price):
    global p1_Wins
    global p2_Wins
    global rounds_played

    p1_absolute_error = round(abs(p1_guess - product_price), 2)
    p2_absolute_error = round(abs(p2_guess - product_price), 2)

    if p1_absolute_error < p2_absolute_error:
        p1_Wins += 1
        os.system("cls")
        print_round_winner("jugador 1")
        say("El primer jugador se ha acercado más. Se ha quedado a {} euros".format(p1_absolute_error))
    elif p1_absolute_error > p2_absolute_error:
        p2_Wins += 1
        os.system("cls")
        print_round_winner("jugador 2")
        say("El segundo jugador se ha acercado más. Se ha quedado a {} euros".format(p2_absolute_error))
    else:  # If both errors are the same
        os.system("cls")
        say("Ambos jugadores se han quedado igual de cerca. Se elegirá un ganador aleatorio.")
        pick_random_winner()
    rounds_played += 1
    return


def print_title():
    title = "EL PRECIO JUSTO by Unai Iglesias"
    print("+" + "-" * len(title) + "+")
    print("|" + title + "|")
    print("+" + "-" * len(title) + "+")
    return


def print_round_counter_and_scoreboard(number_of_rounds):
    global p1_Wins
    global p2_Wins
    global rounds_played
    content = "Ronda " + str(rounds_played + 1) + " / " + str(number_of_rounds)
    scoreboard = "J1 {} --- {} J2".format(p1_Wins, p2_Wins)
    print("+" + "-" * len(content) + "+")
    print("|" + content + "|" + "    " + scoreboard)
    print("+" + "-" * len(content) + "+")
    return


def print_round_winner(round_winner):
    content = "El " + round_winner + " ha ganado esta ronda"
    scoreboard = "J1 {} --- {} J2".format(p1_Wins, p2_Wins)
    print("+" + "-" * len(content) + "+")
    print("|" + content + "|" + "    " + scoreboard)
    print("+" + "-" * len(content) + "+")
    return


def print_winner(winner):
    content = "Ha ganado el " + winner + " ¡Felicidades!"
    scoreboard = "J1 {} --- {} J2".format(p1_Wins, p2_Wins)
    print("+" + "-" * len(content) + "+")
    print("|" + content + "|" + "    " + scoreboard)
    print("+" + "-" * len(content) + "+")
    return


def main():
    # Initialization
    global p1_Wins
    global p2_Wins
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
    while rounds_played < number_of_rounds:
        os.system("cls")

        if rounds_played == 0:  # User will choose category for the first round
            category_link = let_user_choose_category()
        else:
            category_link = get_random_category_link(all_categories)

        print_round_counter_and_scoreboard(number_of_rounds)

        product_name, product_price, product_image_link = proccess_products(session, category_link)

        # Ask for guesses
        p1_guess, p2_guess = ask_and_check_user_guess(product_name, product_image_link, session)

        # Reveal real product price
        product_price_adapted_to_speech = str(round(product_price, 2)).replace(".", "coma")
        say("El precio era {} euros".format(product_price_adapted_to_speech))
        print("El precio era {} €.".format(round(product_price, 2)))

        determine_winner(p1_guess, p2_guess, product_price)

        if rounds_played != number_of_rounds:
            say("Siguiente ronda.")

    if p1_Wins > p2_Wins:
        winner = "primer jugador"
        os.system("cls")
    elif p2_Wins > p1_Wins:
        winner = "segundo jugador"
        os.system("cls")

    print_winner(winner)

    say("Ha ganado el {}. ¡Felicidades!".format(winner))
    os.system("pause")


if __name__ == "__main__":
    main()
