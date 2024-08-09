import pygame
import random
from sys import exit as sys_exit

pygame.init()

pygame.mixer.init()


class Game:
    FPS = 60  # ajusta la velocidad del juego, mientras mas rapido, mas dificil

    def __init__(self):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 660
        self.road_w = self.SCREEN_WIDTH // 1.6
        self.roadmark_w = self.SCREEN_WIDTH // 80
        self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4
        self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4
        self.speed = 3
        self.speed_factor = self.SCREEN_HEIGHT / 660  # anima el auto del enemigo
        self.car_lane = "D"
        self.car2_lane = "I"

        self.GRASS_COLOR = (60, 220, 0)
        self.DARK_ROAD_COLOR = (50, 50, 50)
        self.YELLOW_LINE_COLOR = (255, 240, 60)
        self.WHITE_LINE_COLOR = (255, 255, 255)

        self.score = 0
        self.level = 0

        self.CLOCK = pygame.time.Clock()
        self.event_updater_counter = 0  

        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
        )

        pygame.display.set_caption("Juego de autos en 2D")

        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.score_font = pygame.font.Font("assets/fonts/joystix monospace.otf", 30)
        self.game_info_font = pygame.font.SysFont("Arial", 40)

        # carga de sonido
        self.car_crash_sound = pygame.mixer.Sound("assets/carCrash.wav")

        # carga del auto del jugador
        self.original_car = pygame.image.load("assets/cars/car.png")
        self.car = pygame.transform.scale(
            self.original_car,
            (
                int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car_loc = self.car.get_rect()
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        )

        # carga del auto enemigo
        self.original_car2 = pygame.image.load("assets/cars/otherCar.png")
        self.car2 = pygame.transform.scale(
            self.original_car2,
            (
                int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                int(self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)),
            ),
        )
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = self.left_lane, self.SCREEN_HEIGHT * 0.2

        self.scale = self.SCREEN_HEIGHT - self.car2_loc.height

        self.game_state = "MAIN GAME"
        self.game_paused = False

        self.has_update_scores = False
        self.scores = []

    def main_loop(self):
        while True:
            if self.game_paused:
                self.game_paused_draw()
                self.game_info_draw()
                self.CLOCK.tick(10)
                pygame.display.update()
                self.handle_critical_events()
                continue

            self.event_loop()
            self.event_updater_counter += 1

            if (
                self.event_updater_counter > self.SCREEN_HEIGHT
            ):  # Para la línea punteada, es suficiente con reiniciar
                self.event_updater_counter = 0

            if self.game_state == "GAME OVER":
                self.game_over_draw()
                self.CLOCK.tick(self.FPS)
                pygame.display.update()
                continue

            # si el puntaje pasa los 5000 entonces
            # aumenta la velocidad del auto enemigo
            if self.score % 5000 == 0:
                self.speed += 0.16
                self.level += 1
                print("Mas dificil!")

            self.car2_loc[1] += (
                self.speed * self.speed_factor
            )  # sumando velocidad para cambiar el eje y de car2_loc

            # Si el car2 se mueve y desaparece, entonces cambia la ubicación del nuevo car2
            if self.car2_loc[1] > self.SCREEN_HEIGHT:
                # usando valor al azar entre 0 y 1
                # para alternar la posicion del auto
                if random.randint(0, 1) == 0:
                    self.car2_loc.center = self.right_lane, -200
                    self.car2_lane = "D"
                else:
                    self.car2_loc.center = self.left_lane, -200
                    self.car2_lane = "I"

            # If Cars collide game ends
            if self.car2_loc.colliderect(self.car_loc):
                self.car_crash_sound.play()
                self.game_state = "GAME OVER"

            self.draw(self.event_updater_counter)
            self.display_score()

            self.score += 1

            self.CLOCK.tick(self.FPS)
            pygame.display.update()

    def handle_critical_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_paused = False

    def event_loop(self):
        for event in pygame.event.get():  # bucle de eventos
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT] and self.car_lane == "D":
                    self.car_loc = self.car_loc.move([-int(self.road_w / 2), 0])
                    self.car_lane = "I"
                if event.key in [pygame.K_d, pygame.K_RIGHT] and self.car_lane == "I":
                    self.car_loc = self.car_loc.move([int(self.road_w / 2), 0])
                    self.car_lane = "D"
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed + 5
                if event.key in [pygame.K_SPACE, pygame.K_r] and self.game_state == "GAME OVER":
                    self.restart_game()
                if event.key in [pygame.K_SPACE]:
                    if not self.game_paused:
                        self.game_paused = True
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    self.quit_game()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    self.speed = self.speed - 5
            if event.type == pygame.VIDEORESIZE:
                self.SCREEN_WIDTH, self.SCREEN_HEIGHT = event.w, event.h
                self.SCREEN = pygame.display.set_mode(
                    (self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE
                )

                # Actualiza la posicion de los carriles
                self.road_w = int(self.SCREEN_WIDTH / 1.6)
                self.right_lane = self.SCREEN_WIDTH / 2 + self.road_w / 4
                self.left_lane = self.SCREEN_WIDTH / 2 - self.road_w / 4

                # Redimensiona las imágenes del coche utilizando las imágenes originales
                self.car = pygame.transform.scale(
                    self.original_car,
                    (
                        int(self.original_car.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )
                self.car2 = pygame.transform.scale(
                    self.original_car2,
                    (
                        int(self.original_car2.get_width() * (self.SCREEN_WIDTH / 800)),
                        int(
                            self.original_car2.get_height() * (self.SCREEN_HEIGHT / 600)
                        ),
                    ),
                )

                # Actualiza las posiciones de los rectángulos 
                # del coche basándote en las posiciones actualizadas de los carriles
                if self.car_lane == "R":
                    self.car_loc = self.car.get_rect(
                        center=(self.right_lane, self.SCREEN_HEIGHT * 0.8)
                    )
                else:
                    self.car_loc = self.car.get_rect(
                        center=(self.left_lane, self.SCREEN_HEIGHT * 0.8)
                    )

                if self.car2_lane == "R":
                    self.car2_loc = self.car2.get_rect(
                        center=(self.right_lane, self.car2_loc.center[1])
                    )
                else:
                    self.car2_loc = self.car2.get_rect(
                        center=(self.left_lane, self.car2_loc.center[1])
                    )

    def draw(self, event_updater_counter):
        """
        Esta es una función que dibuja el fondo del juego y se
        utiliza para actualizar el fondo cuando se cambia el 
        tamaño de la ventana. Para mover la línea amarilla 
        punteada en la carretera, se dibujan varios rectángulos
        y luego se mueven con la variable event_updater_counter.
        Una vez que event_update_counter alcanza 30, los rectángulos
        se reinician a sus posiciones originales y el proceso se repite.
        """

        # dibuja la pista en el medio de la pantalla verde
        self.SCREEN.fill(self.GRASS_COLOR)

        pygame.draw.rect(
            self.SCREEN,
            self.DARK_ROAD_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2,
                0,
                self.road_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # dibuja la linea amarilla al centro de la pista
        num_yellow_lines = 11 # 10 + 1 moviendo los bordes de la pantalla
        # event_updater_counter es usado para mover la linea rayada amarilla
        line_positions = [
            (
                self.SCREEN_WIDTH / 2 - self.roadmark_w / 2,
                # Ten cuidado al cambiar estos valores, ya que puede
                # causar que las líneas no se dibujen correctamente. 
                # La velocidad de la línea es el 75% de la velocidad del coche2
                int(
                    (self.SCREEN_HEIGHT / 20
                    + 2 * self.SCREEN_HEIGHT / 20 * num_line
                    + self.speed * self.speed_factor * event_updater_counter * 0.75)
                    % self.SCREEN_HEIGHT / 10 * 11
                    - self.SCREEN_HEIGHT / 20
                ),
                self.roadmark_w,
                self.SCREEN_HEIGHT / 20,
            )
            for num_line in range(num_yellow_lines)
        ]

        for line_position in line_positions:
            pygame.draw.rect(
                self.SCREEN,
                self.YELLOW_LINE_COLOR,
                line_position,
            )

        # dibuja la linea blanca en el lado izquierdo de la pista
        pygame.draw.rect(
            self.SCREEN,
            self.WHITE_LINE_COLOR,
            (
                self.SCREEN_WIDTH / 2 - self.road_w / 2 + self.roadmark_w * 2,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )
        # dibuja la linea blanca en el lado derecho de la pista
        pygame.draw.rect(
            self.SCREEN,
            (255, 255, 255),
            (
                self.SCREEN_WIDTH / 2 + self.road_w / 2 - self.roadmark_w * 3,
                0,
                self.roadmark_w,
                self.SCREEN_HEIGHT,
            ),
        )

        # Pone el auto en la pista
        self.SCREEN.blit(self.car, self.car_loc)
        self.SCREEN.blit(self.car2, self.car2_loc)

    def display_score(self):
        self.message_display(
            "PUNTAJE ",
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            20,
        )
        self.message_display(
            self.score,
            self.score_font,
            (255, 50, 50),
            self.right_lane + self.road_w / 2.5,
            55,
        )

    def game_over_draw(self):
        self.SCREEN.fill((200, 200, 200))
        self.message_display(
            "PERDISTE!", self.game_over_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 330
        )
        self.message_display(
            "PUNTAJE FINAL ",
            self.score_font,
            (80, 80, 80),
            self.SCREEN_WIDTH / 2 - 50,
            230,
        )
        self.message_display(
            self.score, self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2 + 150, 230
        )

        if not self.has_update_scores:
            # Lee high_scores desde un archivo txt, que tiene formato separado por comas
            with open("high_scores.txt", "r") as hs_file:
                high_scores = hs_file.read()
                hs_file.close()

            # Convierte los datos del texto del puntaje más alto en una lista de números y añade el nuevo puntaje a los datos
            self.scores = [int(i) for i in high_scores.split()]
            self.scores.append(self.score)

            # Acomoda en orden descendente, luego solo mantiene los 5 mayores y borra el resto
            self.scores.sort()
            self.scores.reverse()

            if len(self.scores) > 5:
                self.scores = self.scores[:5]

            #formatea los puntajes
            self.scores = self.pad_scores(self.scores)

            # Reescribe los puntajes con las 5 puntajes mas altos
            with open("high_scores.txt", "w") as hs_file:
                hs_file.write(" ".join([str(i) for i in self.scores]))

            self.has_update_scores = True

            # Muestra los 5 mayores puntajes
        self.message_display(
            "Puntajes mas altos", self.score_font, (100, 100, 100), self.SCREEN_WIDTH / 2, 410
        )

        for idx, score in enumerate(self.scores):
            self.message_display(
                f"{idx + 1}. {score}",
                self.score_font,
                (100, 100, 100),
                self.SCREEN_WIDTH / 2,
                410 + ((idx + 1) * 30),
            )
        
        self.message_display(
            "(ESPACIO para Reiniciar)", self.score_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 600
        )

    def game_paused_draw(self):
        self.message_display(
            "PAUSADO", self.game_over_font, (0, 0, 100), self.SCREEN_WIDTH / 2, 200
        )

    def game_info_draw(self):
        pygame.draw.rect(self.SCREEN, (0, 0, 0), [self.SCREEN_WIDTH/4 - 3, self.SCREEN_HEIGHT/4 + 65 - 3, self.SCREEN_WIDTH/2 + 6, 300 + 6])
        pygame.draw.rect(self.SCREEN, (200, 200, 200), [self.SCREEN_WIDTH/4, self.SCREEN_HEIGHT/4 + 65, self.SCREEN_WIDTH/2, 300])
        self.message_display(
            "Controles", self.game_info_font, (40, 40, 40), self.SCREEN_WIDTH / 2, 250
        )
        self.message_display(
            "Izquierda:                 A or \u2190", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 300,
        )
        self.message_display(
            "Derecha:              D or \u2192", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 350,
        )
        self.message_display(
            "Acelera:         W or \u2191", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 400,
        )
        self.message_display(
            "Pausa:        Barra Espaciadora", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 450,
        )
        self.message_display(
            "Salir:              Q o ESC", self.game_info_font, (80, 80, 80), self.SCREEN_WIDTH / 2, 500,
        )

    def restart_game(self):
        self.score = 0
        self.level = 0
        self.speed = 3
        self.event_updater_counter = 0
        self.game_state = "MAIN GAME"
        self.has_update_scores = False
        self.scores = []
        self.car_loc.center = (
            self.right_lane,
            self.SCREEN_HEIGHT - self.car_loc.height * 0.5,
        )
        self.car2_loc = self.car2.get_rect()
        self.car2_loc.center = (self.left_lane, self.SCREEN_HEIGHT * 0.2)
        self.car_lane = "D"
        self.car2_lane = "I"
        print("Reiniciar!")

    @staticmethod
    def quit_game():
        sys_exit()
        quit()

    def message_display(self, text, font, text_col, x, y, center=True):
        """
        Este es el texto a mostrar con las configuraciones deseadas

        param: text: Este es el texto a mostrar
        type: str

        param: font: La fuente a utilizar
        type: Font

        param: text_col: El color del texto en formato RGB
        type: tuple

        param: x: coordenada x del texto
        type: int

        param: y: coordenada y del texto
        type: int

        param: center: Determina si el texto esta centrado
        type: bool
        """
        img = font.render(str(text), True, text_col)
        img = img.convert_alpha()

        if center:
            # Ajusta x, y para centrar el texto
            x -= img.get_width() / 2
            y -= img.get_height() / 2

        self.SCREEN.blit(img, (x, y))

    # rellena de ceros para que los puntajes tengan la misma alineacion
    @staticmethod
    def pad_scores(scores):
        """
        :param: scores : puntajes en orden descendente
        :type: list

        :return: puntajes en formato acomodado
        :type: list
        """
        length_of_highest_score = len(str(scores[0]))
        scores_padded = [str(score).zfill(length_of_highest_score) for score in scores]
        return scores_padded

if __name__ == "__main__":

    game = Game()

    game.main_loop()

