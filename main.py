import pygame
import math
import random
import copy
from constants import *


cell_size = 80
win_height = 12 * cell_size
win_width = win_height + win_height / 12
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Backgammon")


board = [2, 0, 0, 0, 0, -5,
         0, -3, 0, 0, 0, 5,
         -5, 0, 0, 0, 3, 0,
         5, 0, 0, 0, 0, -2]


def board_handler(n_board, mouse_pos, highlight, movable):
    selected_t = -1
    for i in range(0, 24):
        if i <= 5:
            x = i
        elif i <= 11:
            x = i + 1
        elif i <= 17:
            x = 24 - i
        else:
            x = 23 - i
        level = math.floor(i / 12)

        points = [(win_width - x * cell_size, level * win_height),
                  (win_width - (x + 1) * cell_size, level * win_height),
                  (win_width - (x + 0.5) * cell_size, (0.4 + level * 0.2) * win_height)]
        if i % 2 == 0:
            t_color = TRIANGLE_DARK
        else:
            t_color = TRIANGLE_LIGHT
        pygame.draw.polygon(win, t_color, points, False)

        if n_board[i] != 0:
            p_sum = abs(n_board[i])
            if n_board[i] > 0:
                p_color = PIECE_LIGHT
                p_outline = OUTLINE_LIGHT
            else:
                p_color = PIECE_DARK
                p_outline = OUTLINE_DARK

            for p in range(0, p_sum):
                p_pos = (win_width - (x + 0.5) * cell_size,
                         level * win_height + (1 + level * -2) * cell_size / 2 + (1 + level * -2) * p * cell_size)
                pygame.draw.circle(win, p_color, p_pos, cell_size / 2)
                pygame.draw.circle(win, p_outline, p_pos, cell_size / 2, 2)

                if i in movable and p == p_sum - 1:
                    target_rect = pygame.Rect(p_pos, (0, 0)).inflate((cell_size, cell_size))
                    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
                    pygame.draw.circle(shape_surf, HIGHLIGHT_PIECE, (cell_size / 2, cell_size / 2), cell_size / 2)
                    win.blit(shape_surf, target_rect)

        bar_rect = pygame.Rect(win_width / 2 - cell_size / 2, 0, cell_size, win_height)
        pygame.draw.rect(win, BAR_COLOR, bar_rect)
        pygame.draw.rect(win, PIECE_DARK, bar_rect, 2)

        collider_rect = pygame.Rect(win_width - (x + 1) * cell_size, level * 0.55 * win_height,
                                    cell_size, 0.45 * win_height)
        if pygame.Rect.collidepoint(collider_rect, mouse_pos):
            selected_t = i

        if i in highlight:
            lx, ly = zip(*points)
            min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
            target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
            shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
            pygame.draw.polygon(shape_surf, HIGHLIGHT_TRIANGLE, [(x - min_x, y - min_y) for x, y in points])
            win.blit(shape_surf, target_rect)

    return selected_t


def roll():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    if d1 == d2:
        return [d1, d1, d1, d1]
    return [d1, d2]


def dice_handler(dice, used):
    used_sum = 0
    for d in range(0, len(dice)):
        die_rect = pygame.Rect(3 * win_width / 4 - (1 - 1.5 * d + 1.5 * (math.floor(len(dice) / 4))) * cell_size,
                               win_height / 2 - cell_size / 2,
                               cell_size, cell_size)
        color = PIECE_LIGHT
        if dice[d] in used and used_sum < len(used):
            color = DICE_GRAY
            used_sum += 1
        pygame.draw.rect(win, color, die_rect)
        pygame.draw.rect(win, OUTLINE_LIGHT, die_rect, 2)

        if dice[d] in [1, 3, 5]:
            # middle pip
            pygame.draw.circle(win, PIECE_DARK, die_rect.center, cell_size / 15)
        if dice[d] in [2, 4, 5, 6]:
            # top left pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] - cell_size / 4, die_rect.center[1] - cell_size / 4), cell_size / 15)
        if dice[d] in [3, 4, 5, 6]:
            # top right pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] - cell_size / 4, die_rect.center[1] + cell_size / 4), cell_size / 15)
        if dice[d] in [3, 4, 5, 6]:
            # bottom left pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] + cell_size / 4, die_rect.center[1] - cell_size / 4), cell_size / 15)
        if dice[d] in [2, 4, 5, 6]:
            # bottom right pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] + cell_size / 4, die_rect.center[1] + cell_size / 4), cell_size / 15)
        if dice[d] == 6:
            # middle left pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] - cell_size / 4, die_rect.center[1]), cell_size / 15)
            # middle right pip
            pygame.draw.circle(win, PIECE_DARK,
                               (die_rect.center[0] + cell_size / 4, die_rect.center[1]), cell_size / 15)


def generate_moves(n_board, p, dice):
    moves = []
    col = math.copysign(1, n_board[p])
    if p >= 0:
        for die in dice:
            die = int(die * col)
            if p + die in range(0, len(n_board)):
                if n_board[p + die] * n_board[p] >= 0 or abs(n_board[p + die]) == 1:
                    moves.append(p + die)
    return moves


def make_move(old, new):
    col = int(board[old] / abs(board[old]))
    board[old] = board[old] - col
    board[new] = board[new] + (abs(board[new]) + 1) * col
    return new - old


def sub_lists(list1, list2):
    l1, l2 = list1, list2
    for item in l1:
        if item in l2:
            l1.remove(item)
            l2.remove(item)
    return l1


def main():
    turn = 1
    hovering_t = selected_t = -1
    dice = roll()
    used_dice = []
    moves = []

    pygame.init()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hovering_t in moves:
                    used_dice.append(abs(make_move(selected_t, hovering_t)))
                    selected_t = -1
                    if not sub_lists(dice, used_dice):
                        turn *= -1
                        dice = roll()
                        used_dice = []
                else:
                    if board[hovering_t] * turn > 0:
                        selected_t = hovering_t
                    else:
                        selected_t = -1
                moves = generate_moves(board, selected_t, sub_lists(dice, used_dice))

        win.fill(BOARD_COLOR)

        hovering_t = board_handler(board, pygame.mouse.get_pos(), moves, [selected_t])
        dice_handler(dice, used_dice)
        # print(dice, used_dice, sub_lists(dice, used_dice))

        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
