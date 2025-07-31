import pygame
import sys

# Initialization
window_width, window_height = 1500, 800
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('Game BGM.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Nine Men's Morris")
back_image = pygame.image.load(r'Screenshot 2024-10-26 200053.png')
font = pygame.font.Font(None, 50)

larger=pygame.transform.scale(back_image,(window_width,window_height))

# Define colors
White = (255, 255, 255)
P1_Colour = (255, 102, 255)
P2_Colour = (127, 0, 255)
P_Colour = (51,255,255)

# Define variables
game_phase = "placing"
player_turn = 1
piece_count_1 = 0
piece_count_2 = 0
piece_dead_1 = 0
piece_dead_2 = 0
miller = False
removed = False
text4 = "Place Your Piece"
game_over=False
win_time=None

# Mill tracking variables
player1_mills = set()  # Track Player 1's active mills
player2_mills = set()  # Track Player 2's active mills
last_move_mills = set()  # Track mills formed in the last move
processed_mills = set()  # Track mills that have been processed for removal
broken_mills = set()  # Track previously broken mills that can be reformed


# Draw the board
def my_board():
    # Point class for storing details
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.occupied = False
            self.player = None
            self.connections = []

        def occupy(self, player):
            self.occupied = True
            self.player = player

        def vacate(self):
            self.occupied = False
            self.player = None

    h_margin = 150
    v_margin = 40
    o_size = 720
    m_size = 520
    s_size = 320
    gap = 100

    # Define 24 points
    points = [
        Point(h_margin, v_margin), Point(h_margin + o_size // 2, v_margin), Point(h_margin + o_size, v_margin),
        Point(h_margin + gap, v_margin + gap), Point(h_margin + gap + m_size // 2, v_margin + gap),
        Point(h_margin + gap + m_size, v_margin + gap), Point(h_margin + gap * 2, v_margin + gap * 2),
        Point(h_margin + gap * 2 + s_size // 2, v_margin + gap * 2),
        Point(h_margin + gap * 2 + s_size, v_margin + gap * 2),
        Point(h_margin, v_margin + o_size // 2), Point(h_margin + gap, v_margin + o_size // 2),
        Point(h_margin + gap * 2, v_margin + o_size // 2), Point(h_margin + gap * 2 + s_size, v_margin + o_size // 2),
        Point(h_margin + gap * 3 + s_size, v_margin + o_size // 2),
        Point(h_margin + gap * 4 + s_size, v_margin + o_size // 2),
        Point(h_margin + gap * 2, v_margin + gap * 2 + s_size),
        Point(h_margin + gap * 2 + s_size // 2, v_margin + gap * 2 + s_size),
        Point(h_margin + gap * 2 + s_size, v_margin + gap * 2 + s_size), Point(h_margin + gap, v_margin + gap + m_size),
        Point(h_margin + gap + m_size // 2, v_margin + gap + m_size),
        Point(h_margin + gap + m_size, v_margin + gap + m_size),
        Point(h_margin, v_margin + o_size), Point(h_margin + o_size // 2, v_margin + o_size),
        Point(h_margin + o_size, v_margin + o_size)
    ]

    # Draw points and connections on the screen
    connections = [
        (0, 1), (0, 9), (1, 4), (1, 2), (2, 14), (3, 4), (3, 10), (4, 5), (4, 7), (5, 13),
        (6, 7), (6, 11), (7, 8), (8, 12), (9, 10), (9, 21), (10, 11), (10, 18), (11, 15),
        (12, 13), (12, 17), (13, 14), (13, 20), (14, 23), (15, 16), (16, 17), (16, 19),
        (18, 19), (19, 20), (19, 22), (21, 22), (22, 23)
    ]

    for con in connections:
        pygame.draw.line(screen, White, (points[con[0]].x, points[con[0]].y), (points[con[1]].x, points[con[1]].y), 3)
        points[con[0]].connections.append(points[con[1]])
        points[con[1]].connections.append(points[con[0]])

    pygame.draw.circle(screen, P_Colour, (1050, 620), 30)
    pygame.draw.circle(screen, P1_Colour, (1050, 620), 25)
    pygame.draw.circle(screen, P_Colour, (1050, 720), 30)
    pygame.draw.circle(screen, P2_Colour, (1050, 720), 25)

    return points,connections


def is_near(x1, y1, x2, y2):
    threshold = 30
    return abs(x1 - x2) < threshold and abs(y1 - y2) < threshold


def piece_place(player, points, x_mouse, y_mouse):
    for poi in points:
        if not poi.occupied and is_near(x_mouse, y_mouse, poi.x, poi.y):
            poi.occupy(player)
            return True
    return False


selected_point = None


def piece_move(player, points, from_point, to_point):
    if from_point.occupied and from_point.player == player:
        if to_point in from_point.connections and not to_point.occupied:
            to_point.occupy(player)
            from_point.vacate()
            return True
    return False


# Mill connections
mills = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11), (12, 13, 14), (15, 16, 17), (18, 19, 20), (21, 22, 23),
         (0, 9, 21), (3, 10, 18), (6, 11, 15), (1, 4, 7), (16, 19, 22), (8, 12, 17), (5, 13, 20), (2, 14, 23)]


def mill_detector(player, points, mills):
    immune = []
    global player1_mills, player2_mills, last_move_mills, miller, processed_mills, broken_mills
    new_mill_formed = False
    current_player_mills = set()

    # Find all current mills for the player
    for mil in mills:
        if points[mil[0]].player == points[mil[1]].player == points[mil[2]].player == player:
            mill_tuple = tuple(sorted([id(points[mil[0]]), id(points[mil[1]]), id(points[mil[2]])]))
            current_player_mills.add(mill_tuple)
            immune.extend([points[mil[0]], points[mil[1]], points[mil[2]]])

            # Check if this is a new mill or a reformed mill
            if player == 1:
                if mill_tuple not in player1_mills or mill_tuple in broken_mills:
                    player1_mills.add(mill_tuple)
                    if mill_tuple not in processed_mills or mill_tuple in broken_mills:
                        new_mill_formed = True
                        last_move_mills.add(mill_tuple)
                        broken_mills.discard(mill_tuple)  # Remove from broken mills if it was there
            else:
                if mill_tuple not in player2_mills or mill_tuple in broken_mills:
                    player2_mills.add(mill_tuple)
                    if mill_tuple not in processed_mills or mill_tuple in broken_mills:
                        new_mill_formed = True
                        last_move_mills.add(mill_tuple)
                        broken_mills.discard(mill_tuple)  # Remove from broken mills if it was there

    return immune, new_mill_formed


def draw_mills(screen, points):
    # Draw Player 1's mills in Red
    for mill_tuple in player1_mills:
        mill_points = []
        for point in points:
            if id(point) in mill_tuple:
                mill_points.append(point)
        if len(mill_points) == 3:
            pygame.draw.line(screen, P1_Colour,
                             (mill_points[0].x, mill_points[0].y),
                             (mill_points[2].x, mill_points[2].y), 10)

    # Draw Player 2's mills in Blue
    for mill_tuple in player2_mills:
        mill_points = []
        for point in points:
            if id(point) in mill_tuple:
                mill_points.append(point)
        if len(mill_points) == 3:
            pygame.draw.line(screen, P2_Colour,
                             (mill_points[0].x, mill_points[0].y),
                             (mill_points[2].x, mill_points[2].y), 10)

def check_broken_mills(points):
    """Check and remove any mills that are no longer valid"""
    global player1_mills, player2_mills, broken_mills

    # Check Player 1's mills
    invalid_mills_p1 = set()
    for mill_tuple in player1_mills:
        mill_points = []
        for point in points:
            if id(point) in mill_tuple:
                mill_points.append(point)
        if len(mill_points) != 3 or any(p.player != 1 for p in mill_points):
            invalid_mills_p1.add(mill_tuple)
            broken_mills.add(mill_tuple)  # Add to broken mills when a mill is broken
    player1_mills -= invalid_mills_p1

    # Check Player 2's mills
    invalid_mills_p2 = set()
    for mill_tuple in player2_mills:
        mill_points = []
        for point in points:
            if id(point) in mill_tuple:
                mill_points.append(point)
        if len(mill_points) != 3 or any(p.player != 2 for p in mill_points):
            invalid_mills_p2.add(mill_tuple)
            broken_mills.add(mill_tuple)  # Add to broken mills when a mill is broken
    player2_mills -= invalid_mills_p2


def remove_opponent_piece(player, points, piece_dead_1, piece_dead_2, x_mouse, y_mouse):
    global processed_mills, miller, broken_mills
    immune, _ = mill_detector(3 - player, points, mills)
    all_pieces_in_mill = True

    # Check if all remaining opponent pieces are in mills
    for poi in points:
        if poi.occupied and poi.player == 3 - player and poi not in immune:
            all_pieces_in_mill = False
            break

    for poi in points:
        if poi.occupied and poi.player == 3 - player and is_near(x_mouse, y_mouse, poi.x, poi.y):
            if poi not in immune or all_pieces_in_mill:
                if 3 - player == 1:
                    piece_dead_1 += 1
                else:
                    piece_dead_2 += 1
                poi.vacate()
                processed_mills.update(last_move_mills)
                last_move_mills.clear()
                miller = False
                check_broken_mills(points)  # Check for newly broken mills
                return piece_dead_1, piece_dead_2, True
    return piece_dead_1, piece_dead_2, False

def check_win(player,game_phase, piece_count_1, piece_count_2, piece_dead_1, piece_dead_2,connections,points):
    if game_phase == "moving":
        if (piece_count_1 - piece_dead_1) < 3:
            return 2  # Player 2 wins
        elif (piece_count_2 - piece_dead_2) < 3:
            return 1  # Player 1 wins
        j=True
        for poi in points:
            if poi.player == player and poi.occupied :
                for con in poi.connections:
                    if con.occupied == False:
                        j=False
                        break
            if not j:
                break
        if j:
            return 3-player
    return None

def draw_highlights(screen, selected_point, points, game_phase):
    if selected_point and game_phase == "moving":
        # Highlight selected piece
        pygame.draw.circle(screen, (0, 255, 0), (selected_point.x, selected_point.y), 35)
        # Highlight possible moves
        for con in selected_point.connections:
            if not con.occupied:
                pygame.draw.circle(screen, P_Colour, (con.x, con.y), 20)



points,connections = my_board()

# Main game loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x_posi, y_posi = pygame.mouse.get_pos()
            if game_phase == "placing":
                if miller:
                    piece_dead_1, piece_dead_2, removed = remove_opponent_piece(
                        player_turn, points, piece_dead_1, piece_dead_2, x_posi, y_posi
                    )
                    if removed:
                        text4 = "Place Your Piece"
                        processed_mills.update(last_move_mills)  # Add the current mill to processed mills
                        last_move_mills.clear()  # Clear last move mills
                        miller = False  # Reset miller flag
                        player_turn = 2 if player_turn == 1 else 1

                        if (piece_count_1 + piece_count_2 == 18) and (piece_count_1 - piece_dead_1 >= 3) and (piece_count_2 - piece_dead_2 >= 3):
                            game_phase = "moving"
                            text4="Move Your Piece"
                else:
                    if piece_place(player_turn, points, x_posi, y_posi):
                        text4="Place Your Piece"
                        if player_turn == 1:
                            piece_count_1 += 1
                        else:
                            piece_count_2 += 1

                        _, new_mill_formed = mill_detector(player_turn, points, mills)
                        if new_mill_formed:
                            miller = True
                            text4 = "Remove Opponent's Piece"
                        else:
                            player_turn = 2 if player_turn == 1 else 1

                        if (piece_count_1 + piece_count_2 == 18) and (piece_count_1 - piece_dead_1 >= 3) and (piece_count_2 - piece_dead_2 >= 3):
                            game_phase = "moving"
                            text4="Select your piece to move"

            # And similarly modify the moving phase section:
            elif game_phase == "moving":
                if miller:
                    piece_dead_1, piece_dead_2, removed = remove_opponent_piece(
                        player_turn, points, piece_dead_1, piece_dead_2, x_posi, y_posi
                    )
                    if removed:
                        processed_mills.update(last_move_mills)  # Add the current mill to processed mills
                        last_move_mills.clear()  # Clear last move mills
                        miller = False  # Reset miller flag
                        player_turn = 2 if player_turn == 1 else 1
                        text4="Select your piece to move"
                elif selected_point:
                    text4="Select your piece to move"
                    for poi in points:
                        if is_near(x_posi, y_posi, poi.x, poi.y):
                            if piece_move(player_turn, points, selected_point, poi):
                                selected_point = None
                                _, new_mill_formed = mill_detector(player_turn, points, mills)
                                if new_mill_formed:
                                    miller = True
                                    text4 = "Remove Opponent's Piece"
                                else:
                                    player_turn = 2 if player_turn == 1 else 1
                                break
                else:
                    text4 = "Select the destination"
                    for poi in points:
                        if poi.occupied and poi.player == player_turn and is_near(x_posi, y_posi, poi.x, poi.y):
                            selected_point = poi
                            break

    winner = check_win(player_turn,game_phase, piece_count_1, piece_count_2, piece_dead_1, piece_dead_2,connections,points)
    if winner:
        text4=f"Player {winner} wins the game"
        win_time=pygame.time.get_ticks()
        game_over=True

    if game_over and (pygame.time.get_ticks()-win_time) >= 10000 :
            run=False

    screen.fill((0, 0, 0))
    screen.blit(larger, (0, 0))
    my_board()
    check_broken_mills(points)  # Check for broken mills
    draw_mills(screen, points)  # Draw all active mills
    draw_highlights(screen, selected_point, points, game_phase)

    # Denoting player turn
    text1 = f"Player 1: {piece_count_1 - piece_dead_1}"
    text2 = f"Player 2: {piece_count_2 - piece_dead_2}"

    #Denoting the process
    text3 = f"Player Turn: {player_turn}"
    text5 = "Event: "



    text1_surface = font.render(text1, True, White)
    text2_surface = font.render(text2, True, White)
    text3_surface = font.render(text3, True, White)
    text4_surface = font.render(text4, True, White)
    text5_surface = font.render(text5, True, White)



    screen.blit(text1_surface, (1100, 600))
    screen.blit(text2_surface, (1100, 700))
    screen.blit(text3_surface, (900, 250))
    screen.blit(text4_surface, (1020, 300))
    screen.blit(text5_surface, (900, 300))

    for poi in points:
        if poi.player == 1:
            pygame.draw.circle(screen, P_Colour, (poi.x, poi.y), 30)
            pygame.draw.circle(screen, P1_Colour, (poi.x, poi.y), 25)
        elif poi.player == 2:
            pygame.draw.circle(screen, P_Colour, (poi.x, poi.y), 30)
            pygame.draw.circle(screen, P2_Colour, (poi.x, poi.y), 25)
        else:
            pygame.draw.circle(screen, White, (poi.x, poi.y), 15)

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()
sys.exit()