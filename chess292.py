import re
"""
we used global constants to denote special conditions like cpture, castling, piece color, capture and checkmate
"""
WHITE = "w"
BLACK = "b"
SPACE = " "
CASTLING = "O"
capture_ = "x"
check_mate = "+"
    
def setup():
    """This function was used to create 2 dictionaries boardview and pieceview which are used to denote the position of the pieces and the piece in a particular position

    Returns:
        [dict, dict] -- [The 2 dictionaries board_view and piece_view denote the initial board setup ]
    """    
    squares = [y+x for x in "12345678" for y in "abcdefgh"]
    start = "RNBQKBNR" + "P" * 8 + " " * 32 + "p" * 8 + "rnbqkbnr"
    board_view = {square: piece for square, piece in zip(squares, start)}

    piece_view = {_: [] for _ in "BKNPQRbknpqr"}
    for sq in board_view:
        piece = board_view[sq]
        if piece != " ":
            piece_view[piece].append(sq)
    return board_view, piece_view

def display_board(board_view):
    """The display_board function takes a dictionary of positions and pieces corresponding to them as argument and displays them in an easy to understand format.

    Arguments:
        board_view {dict} -- dictionary of positions and pieces corresponding to those positions
    """   
    board = [piece for square, piece in board_view.items()]
    for i in range(56, -1, -8):
        print(board[i: i + 8])

def pgn_to_moves(game_file: str) -> [str]:
    """This function reads a pgn file in order to get the moves made in the game. It first removes uneccesary details and then seperates the moves.

    Arguments:
        game_file {str} -- game_file is a .txt file from wwhich the data is extracted in form of strings

    Returns:
        [str] -- a list of moves is returned
    """
    raw_pgn = " ".join([line.strip() for line in open(game_file)])

    comments_marked = raw_pgn.replace("{", "<").replace("}", ">")
    STRC = re.compile("<[^>]*>")
    comments_removed = STRC.sub(" ", comments_marked)

    STR_marked = comments_removed.replace("[", "<").replace("]", ">")
    str_removed = STRC.sub(" ", STR_marked)

    MOVE_NUM = re.compile("[1-9][0-9]* *\.")
    just_moves = [_.strip() for _ in MOVE_NUM.split(str_removed)]

    last_move = just_moves[-1]
    RESULT = re.compile("( *1 *- *0 *| *0 *- *1 *| *1/2 *- *1/2 *)")
    last_move = RESULT.sub("", last_move)
    moves = just_moves[:-1] + [last_move]

    return [_ for _ in moves if len(_) > 0]

def pre_process_a_move(move: str) -> (str, str):
    """This function processes all the moves in order to seperate the moves made by the white and the black pieces.

    Arguments:
        move {str} -- denotes the move made eg."Rd4"

    Returns:
        (str, str) -- a tuple of move made by white piece and move made by black piece.
    """
    wmove, bmove = move.split()
    if wmove[0] in "abcdefgh":
        wmove = "P" + wmove
    if bmove[0] in "abcdefgh":
        bmove = "p" + bmove
    else:
        bmove = bmove.lower()
    return wmove, bmove

def pre_process_moves(moves: [str]) -> [(str, str)]:
    """This function pre processes all the moves .

    Returns:
        [(str, str)] -- A list of tuples contaning moves made by white and black pieces.
    """
    return [pre_process_a_move(move) for move in moves]

def change_position(piece, position_from, position_to, board_view, piece_view):
    """This function is used to shift a piece from one position to another by altering board_view and piece_view.

    Arguments:
        piece {str} -- denotes the piece to be moved
        position_from {str} -- denotes the current position of the piece
        position_to {str} -- denotes the position the piece is to be moved to
        board_view {dict} -- A dictionry with the piece position as key corresponding to piece
        piece_view {dict} -- A dictionary with piece as key corresponding to a list of positions of the piece.

    Returns:
        dict, dict -- the board_view and piece_view are returned after being updated.
    """
    piece_view[piece].remove(position_from)
    piece_view[piece].append(position_to)
    board_view[position_from] = " "
    board_view[position_to] = piece
    return board_view, piece_view


def is_capture(move):
    """Checks if a piece is being captured during the move

    Arguments:
        move {str} -- Denotes the move made

    Returns:
        boolean value -- returns True if piece is captured else false
    """
    return re.fullmatch("[Pp][a-h]x?[a-h][2-7]?", move) is not None


def is_promotion(move):
    """Checks for pawn promotion

    Arguments:
        move {str} -- denotes the move made

    Returns:
        boolean value -- returns True is pawn is promoted else returns False.
    """
    return re.fullmatch("[Pp][a-h]([18]|x[a-h][18])[RNBQrnbq]", move) is not None
    

def ambiguous_move(piece, extra, destination, board_view, piece_view):
    """Moves the piece denoted to be moved if more than one piece are eligible to be moved.

    Arguments:
        piece {str} -- piece to be moved
        extra {str} -- denotes the current file of the piece to be moved
        destination {str} -- position to which piece is moved
        board_view {dict} -- A dictionry with the piece position as key corresponding to piece
        piece_view {dict} -- A dictionary with piece as key corresponding to a list of positions of the piece.
    Returns:
        dict, dict -- updated piece_view and board_view after the piece is moved
    """
    for current_pos in piece_view[piece]:
        if current_pos[0] == extra:
            return change_position(piece, current_pos, destination, board_view, piece_view)


def castle(color_,  move, board_view, piece_view):
    """This function is used to make the castling move

    Arguments:
        color_ {str} -- denotes the color of the piece
        move {str} -- denotes the move to be made
        board_view {dict} -- A dictionry with the piece position as key corresponding to piece
        piece_view {dict} -- A dictionary with piece as key corresponding to a list of positions of the piece.

    Returns:
        dict, dict -- updated piece_view and board_view after the piece is moved
    """
    king_rook = "kr"
    if color_ == WHITE:
        king_rook = king_rook.upper()
    move_to_rank = piece_view[king_rook[0]][0][1]

    if move.upper() == "O-O":
        move_k_to_file, move_r_to_file = "g", "f"
        rook_position = piece_view[king_rook[1]][1]
    else:
        move_k_to_file, move_r_to_file = "c", "d"
        rook_position = piece_view[king_rook[1]][0]
        
    board_view, piece_view = change_position(king_rook[0], piece_view[king_rook[0]]
                    [0], move_k_to_file + move_to_rank, board_view, piece_view )
    board_view, piece_view = change_position(king_rook[1], rook_position, move_r_to_file + move_to_rank, board_view, piece_view)
    return board_view, piece_view


def kqrnbp_move(move, color_,  board_view, piece_view):
    """This function is used to move a piece if it is a normal move, i.e. no castling, ambiguity etc
    Arguments:
        move {str} -- denotes the move to be made
        color_ {str} -- denotes the color of the piece to be moved 
        board_view {dict} -- A dictionry with the piece position as key corresponding to piece
        piece_view {dict} -- A dictionary with piece as key corresponding to a list of positions of the piece.

    Returns:
        dict, dict -- updated piece_view and board_view after the piece is moved
    """
    piece, extra, destination = move[0], move[1:-2], move[-2:]
    pieces = "rnbqkp"

    if color_ == WHITE:
        pieces = pieces.upper()

    def move_diff(current_pos, destination):
        """Is used to find the shift in rank and file when the move is made
        Arguments:
            current_pos {str} -- denotes the current position of the piece to be moved
            destination {str} -- denotes the position the piece is to be moved to

        Returns:
            int, int -- shift in rank and file
        """
        return abs(ord(destination[0]) - ord(current_pos[0])), abs(ord(current_pos[1]) - ord(destination[1]))

    def can_rook_move():
        """Checks condition for rook's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """
        return moved_by[0] == 0 or moved_by[1] == 0

    def can_knight_move():
        """Checks condition for knight's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """  
        return moved_by in [(1, 2), (2, 1)]

    def can_bishop_move():
        """Checks condition for bishop's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """
        return moved_by[0] == moved_by[1]

    def can_queen_move():
        """Checks condition for queen's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """
        return can_rook_move() or can_bishop_move()

    def can_king_move():
        """Checks condition for king's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """
        return moved_by in [(0, 1), (1, 0), (1, 1)]

    def can_pawn_move():
        """Checks condition for pawn's movement

        Returns:
            boolean value -- returns True if piece can be moved else False
        """
        position_pawn_in_starting = "27"
        if is_capture(move):
            return moved_by in [(1, 1)]
        elif current_pos[1] in position_pawn_in_starting:
            return moved_by in [(0, 1), (0, 2)]
        else:
            return moved_by in [(0, 1)]

    piece_moves = {pieces[0]: can_rook_move, pieces[1]: can_knight_move,  pieces[2]: can_bishop_move,
                   pieces[3]: can_queen_move, pieces[4]: can_king_move, pieces[5]: can_pawn_move}

    for current_pos in piece_view[piece]:
        moved_by = move_diff(current_pos, destination)
        if piece_moves[piece]():
            change_position(piece, current_pos, destination, board_view, piece_view)
            return board_view, piece_view

def make_move(color_, move, board_view, piece_view):
    """The function evaluates the move and decides which move to make , for eg. castling, normal move, etc.

    Arguments:
        color_ {str} -- denotes the color of the piece
        move {str} -- denotes the move to be made
        board_view {dict} -- A dictionry with the piece position as key corresponding to piece
        piece_view {dict} -- A dictionary with piece as key corresponding to a list of positions of the piece.

    Returns:
        dict, dict -- updated piece_view and board_view after the piece is moved
    """  
    piece, extra, destination = move[0], move[1:-2], move[-2:]
    if move[-1] == check_mate:
        move = move.replace(check_mate, "")

    if CASTLING in move.upper():
        board_view, piece_view = castle(color_, move, board_view, piece_view)

    elif extra in "abcdefgh" and len(extra) == 1:
        board_view, piece_view = ambiguous_move(piece, extra[-1], destination, board_view, piece_view)

    elif len(extra) == 2:
        if piece.upper() == "P":
            board_view, piece_view = ambiguous_move(piece, extra[0], destination, board_view, piece_view)
        else:
            board_view, piece_view = ambiguous_move(piece, extra[1], destination, board_view, piece_view)
    elif extra in "abcdefgh" and len(extra) == 1:
        board_view, piece_view = ambiguous_move(piece, extra, destination, board_view, piece_view)
    else:
        board_view, piece_view = kqrnbp_move(move, color_,  board_view, piece_view)
    return board_view, piece_view 

def set_positions_in_board(game_file):
    """This function takes the pgn file of the game and processes it in order to get the moves made and implement them on the chess board.

    Arguments:
        game_file {.txt file} -- A PGN file that contains the details of the chess game

    Returns:
        dict -- A ditionary with the position as key corresponding to the piece in that position.
    """
    board_view, piece_view = setup()
    moves = pre_process_moves(pgn_to_moves(game_file))
    for move in moves:
        wmove, bmove = move
        board_view, piece_view = make_move(WHITE, wmove, board_view, piece_view)
        board_view, piece_view = make_move(BLACK, bmove, board_view, piece_view)
    return board_view


board_view = set_positions_in_board("/home/srishti/my_project/pgn2.txt")


display_board(board_view)