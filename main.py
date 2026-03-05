import arcade
from src.ui.game_window import GameWindow


def main():
    window = GameWindow("Dino")   #Crée la fenêtre et initialise tout
    arcade.run()            #Lance une boucle infinie du jeu


if __name__ == "__main__":
    main()
