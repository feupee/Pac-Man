import pygame

import config


class Pacman:
    """Controla somente o estado e o comportamento do jogador."""

    def __init__(self, images):
        self.images = images
        self.x_pos = config.PLAYER_START_X
        self.y_pos = config.PLAYER_START_Y
        self.direction = config.PLAYER_START_DIRECTION
        self.speed = config.PLAYER_SPEED

    @property
    def center_x(self):
        return self.x_pos + 23

    @property
    def center_y(self):
        return self.y_pos + 24

    def draw(self, screen, counter):
        # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
        current_image = self.images[counter // 7]

        if self.direction == 0:
            screen.blit(current_image, (self.x_pos, self.y_pos))
        elif self.direction == 1:
            screen.blit(pygame.transform.flip(current_image, True, False), (self.x_pos, self.y_pos))
        elif self.direction == 2:
            screen.blit(pygame.transform.rotate(current_image, 90), (self.x_pos, self.y_pos))
        elif self.direction == 3:
            screen.blit(pygame.transform.rotate(current_image, 270), (self.x_pos, self.y_pos))

    def check_position(self, level):
        turns = [False, False, False, False]
        num1 = config.CELL_HEIGHT
        num2 = config.CELL_WIDTH
        num3 = 15
        centerx = self.center_x
        centery = self.center_y

        # check collisions based on center x and center y of player +/- fudge number
        if centerx // config.CELL_WIDTH < config.BOARD_COLUMNS - 1:
            if self.direction == 0:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
            if self.direction == 1:
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
            if self.direction == 2:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
            if self.direction == 3:
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= centerx % num2 <= 18:
                    if level[(centery + num3) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num3) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num2) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num2) // num2] < 3:
                        turns[0] = True
            if self.direction == 0 or self.direction == 1:
                if 12 <= centerx % num2 <= 18:
                    if level[(centery + num1) // num1][centerx // num2] < 3:
                        turns[3] = True
                    if level[(centery - num1) // num1][centerx // num2] < 3:
                        turns[2] = True
                if 12 <= centery % num1 <= 18:
                    if level[centery // num1][(centerx - num3) // num2] < 3:
                        turns[1] = True
                    if level[centery // num1][(centerx + num3) // num2] < 3:
                        turns[0] = True
        else:
            turns[0] = True
            turns[1] = True

        return turns

    def move(self, turns_allowed):
        # r, l, u, d
        if self.direction == 0 and turns_allowed[0]:
            self.x_pos += self.speed
        elif self.direction == 1 and turns_allowed[1]:
            self.x_pos -= self.speed
        if self.direction == 2 and turns_allowed[2]:
            self.y_pos -= self.speed
        elif self.direction == 3 and turns_allowed[3]:
            self.y_pos += self.speed

    def check_pellet_collisions(self, level, score, powerup, power_counter, eaten_ghosts):
        num1 = config.CELL_HEIGHT
        num2 = config.CELL_WIDTH

        if 0 < self.x_pos < config.BOARD_WIDTH - config.CELL_WIDTH:
            if level[self.center_y // num1][self.center_x // num2] == 1:
                level[self.center_y // num1][self.center_x // num2] = 0
                score += 10
            if level[self.center_y // num1][self.center_x // num2] == 2:
                level[self.center_y // num1][self.center_x // num2] = 0
                score += 50
                powerup = True
                power_counter = 0
                eaten_ghosts = [False, False, False, False]

        return score, powerup, power_counter, eaten_ghosts

    def apply_tunnel_wrap(self):
        if self.x_pos > config.BOARD_WIDTH:
            self.x_pos = -47
        elif self.x_pos < -50:
            self.x_pos = config.BOARD_WIDTH - 3

    def reset_position(self):
        self.x_pos = config.PLAYER_START_X
        self.y_pos = config.PLAYER_START_Y
        self.direction = config.PLAYER_START_DIRECTION
