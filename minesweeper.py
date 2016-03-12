import argparse  # mandatory
import random

class GameStatus(object):
    """Enum of possible Game statuses."""
    __init__ = None
    NotStarted, InProgress, Win, Lose = range(4)


class RippleTypes(object):
    """Enum of possible ripple types."""
    __init__ = None
    Simple, Recursive, Queue = range(3)


class SizeOutOfBoundException(Exception):
    pass


class ScatterException(Exception):
    pass


class BoardFormatException(Exception):
    pass


class DimensionsMismatchException(Exception):
    pass


class IllegalIndicesException(Exception):
    pass


class IllegalMoveException(Exception):
    pass


class Board(object):
    """Represents a board of minesweeper game and its current progress."""

    def __init__(self, rows, columns):
        """Initializes an empty hidden board.

        The board will be in the specified dimensions, without mines in it,
        and all of its cells are in hidden state.

        Args:
            rows: the number of rows in the board
            columns: the number of columns in the board

        Returns:
            None (alters self)

        Raises:
            SizeOutOfBoundException if one of the arguments is non positive,
            or the board size is smaller than 1x2 (rows first) or larger than
            20x50.

        """
        if rows < 1 or rows > 20 or columns < 2 or columns > 50:
            raise SizeOutOfBoundException
        
        self.rows, self.columns = rows, columns
        self.startState = True
        self.board = {}
        self.uncovered = []
        cells = [(r,c) for r in range(self.rows) for c in range(self.columns)]
        for (r,c) in cells:
            self.board.update({(r,c):0})

    def getRows(self):
        return self.rows

    def getColumns(self):
        return self.columns

    def getUncoveredCells(self):
        return self.uncovered

    def updateCell(self, r, c):
        neighbors = [(r-1, c-1), (r-1, c), (r-1, c+1), (r, c-1), (r, c+1), (r+1, c-1), (r+1, c), (r+1, c+1)]
        neighbors = [(row, col) for (row, col) in neighbors if (row, col) in self.board.keys()]
        self.board[(r,c)] = len([(row, col) for (row, col) in neighbors if self.board[(row, col)] == '*'])

    def put_mines(self, mines):
        """Randomly scatter the requested number of mines on the board.

        At the beggining, all cells on the board are hidden and with no mines
        at any of them. This method scatters the requested number of mines
        throughout the board randomly, only if the board is in the beginning
        state (as described here). A cell can host only one mine.
        This method not only scatters the mines on the board, but also updates
        the cells around it (so they will hold the right digit).

        Args:
            mines: the number of mines to scatter

        Returns:
            None (alters self)

        Raises:
            ScatterException if the number of mines is smaller than 1 or larger
            than (rows*columns - 1), and if the board is not in beginning state
            If an exception is raised, the board should be in the same state
            as before calling this method.

        """

        if mines < 1 or mines > (self.rows*self.columns-1) or (not self.startState):
            raise ScatterException
        
        for i in range(mines):
            scattered = False
            while not scattered:
                r = random.randint(0, self.rows-1)
                c = random.randint(0, self.columns-1)
                if self.board[(r,c)] != '*':
                    self.board[(r,c)] = '*'
                    scattered = True

        for (r,c) in self.board.keys():
            if self.board[(r,c)] != '*':
                self.updateCell(r, c)
        
        self.startState = False

    def load_board(self, lines):
        """Loads a board from a sequence of lines.

        This method is used to load a saved board from a sequence of strings
        (that usually represent lines). Each line represents a row in the table
        in the following format:
            XY XY XY ... XY
        Where X is one of the characters: 0-8, * and Y is one of letters: H, S.
        0-8 = number of adjusting mines (0 is an empty, mine-free cell)
        * = represents a mine in this cell
        H = this cell is hidden
        S = this cell is uncovered (can be seen)

        The lines can have multiple whitespace of any kind before and after the
        lines of cells, but between each XY pair there is exactly one space.
        Empty or whitespace-only lines are possible everywhere, even between
        valid lines, or after/before them. It is safe to assume that the
        values are correct (the number represents the number of mines around
        a given cell) and the number of mines is also legal.
        Also note that the combination of '0S' is legal.

        Note that this method doesn't get the first two rows of the file (the
        dimensions) on purpose - they are handled in __init__.

        Args:
            lines: a sequence (list or tuple) of lines with the above
            restrictions

        Returns:
            None (alters self)

        Raises:
            BoardFormatException if the lines are empty (all of them),
            or there are wrong X/Y values etc.
            DimensionsMismatchException if the number of valid lines is
            different than the Board dimensions, or if the number of cells per
            row is unequal on different lines, or different from the Board
            dimensions.
            In case both exceptions are possible, BoardFormatException is
            raised.
            If an exception is raised, it's OK if the board is in an
            unstable state (partly copied).

        """
        lines = [line.strip() for line in lines if line.strip() != '']    
        if lines == []:
            raise BoardFormatException

        legalValues = ['0','1','2','3','4','5','6','7','8','*']
        legalStates = ['H', 'S']
        newBoard, newUncovered, pairs = {}, [], []

        dimensionsError = False
        if len(lines) != self.rows:
            dimensionsError = True

        for r in range(len(lines)):
            pairs = lines[r].split(' ')
            if len(pairs) != self.columns:
                dimensionsError = True
            for c in range(len(pairs)):
                elements = list(pairs[c])
                if len(elements) != 2: 
                    raise BoardFormatException
                if elements[0] not in legalValues or elements[1] not in legalStates:
                    raise BoardFormatException
                
                if elements[0] == '*':
                    newBoard.update({(r,c):elements[0]})
                else:
                    newBoard.update({(r,c):int(elements[0])})
                
                if elements[1] == 'S':
                    newUncovered.append((r,c))

        if dimensionsError:
            raise DimensionsMismatchException
        
        self.board = newBoard
        self.uncovered = newUncovered

    def save_board(self, filename):
        """Saves a Board object to a text file.

        Saves the current Board (self) to a file in the following format:
            line 1:#rows of board
            line 2:#columns of board
            line 3:board row #1
            line 4:board row #2
            ...
        where #rows and #columns are integers representing the dimensions of
        the Board, and the rest of the lines are the rows of the Board
        formatted as described in load_board().
        You can include whitespace before/after every value (including #rows
        and #columns), and include empty or whitespace-only lines everywhere,
        including at the start/end of the file, and between any two lines.

        Args:
            filename: the file name (as string) to write to, can be absolute
            or relative path, or even illegal.

        Returns:
            None (and doesn't alters self)

        Raises:
            IOError in case of any file/IO related problem (forward exception
            and don't handle it)

        """
        document = open(filename, 'w')
        document.write(str(self.rows) + '\n')
        document.write(str(self.columns) + '\n')

        lines = []

        for r in range(self.rows):
            line = ''
            for c in range(self.columns):
                value = self.board[(r,c)]
                state = 'H'
                if (r,c) in self.uncovered:
                    state = 'S'
                line += str(value) + state + ' '
            line += '\n'
            lines.append(line)

        document.writelines(lines)

    def get_value(self, row, column):
        """Returns the value of the cell at the given indices.

        The return value is a string of one character, out of 0-8 + '*'.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            If the cell is empty and has no mines around it, return '0'.
            If it has X mines around it (and none in it), return 'X' (digit
            character between 1-8).
            If it has a mine in it return '*'.

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        if (row, column) not in self.board.keys():
            raise IllegalIndicesException
        return str(self.board[(row, column)])

    def is_hidden(self, row, column):
        """Returns if the given cell is in hidden or uncovered state.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            'H' if the cell is hidden, or 'S' if it's uncovered (can be seen).

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        retval = 'H'
        if (row, column) not in self.board.keys():
            raise IllegalIndicesException
        if (row, column) in self.uncovered:
            retval = 'S'
        return retval

    def uncover(self, row, column):
        """Changes the status of a cell from hidden to seen.

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            None (alters self)

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).
            IllegalMoveException if the cell was already uncovered before
            (and the indices given are legal).

        """
        if (row, column) not in self.board.keys():
            raise IllegalIndicesException
        if (row, column) in self.uncovered:
            raise IllegalMoveException
        self.uncovered.append((row, column))

    def get_ripple_type(self):
        """Returns the ripple type of the current board.

        Please note that this method should return a constant value, depending
        on your implementation, and not on some board configurations.

        Returns:
            one of RippleType values (Simple, Recursive or Queue).
        """
        return RippleTypes.Queue
    
    def ripple_sequence(self, row, column):
        """Returns the ripple sequence starting on the specified cell.

        Ripple sequence is the sequence of cells to be uncovered when the cell
        in the row/column position is uncovered. Rippling, for each of the 3
        methods, starts at the upper line (if not the upper row and still
        uncovered) and then moves in a clockwise direction (again, if not on an
        edge row/column or already uncovered).
        For example (we will denote r,c as abbreviations):
            Simple: [(r-1, c), (r-2, c), ... , (r, c+1), (r, c+2) ...] and
                continues over row r and column c.
            Recursive: [(r-1, c), *ripple_sequence(r-1, c), (r, c+1),
                        *ripple_sequence(r, c+1), ...]
                Note that a cell can't appear in the ripple sequence more than
                once.
            Queue: [(r-1, c), (r-1, c+1), ... , according to BFS queue]
        If some direction has no rippling cells (=the cell is on an edge)
        then it is simply skipped. If the given cell has mines around it or
        there are no cells to ripple, return an empty sequence (e.g. []).

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            A sequence of (r,c) tuples (both integers) to ripple, or empty
            sequence in case there's nothing to ripple. Note this doesn't
            alters self.

        Raises:
            IllegalIndicesException if rows/columns/both is out of bounds
            (below 0 or larger than max row/column).

        """
        sequence = []

        if self.get_value(row, column) != '0':
            return sequence

        queue = [(row, column)]
        
        while queue != []:
            for i in range(len(queue)):
                r, c = queue[0]
                del queue[0]
                
                if self.get_value(r, c) == '0':
                    neighbors = [(r-1, c), (r-1, c+1), (r, c+1), (r+1, c+1)]
                    neighbors += [(r+1, c), (r+1, c-1), (r, c-1), (r-1, c-1)]
                
                    for (r,c) in neighbors:
                        condition1 = (r,c) in self.board.keys() and (r,c) not in sequence
                        condition2 = (r,c) != (row, column) and (r,c) not in self.uncovered
                        if condition1 and condition2:
                            sequence.append((r,c))
                            queue.append((r,c))
        
        return sequence

class Game(object):
    """Handles a game of minesweeper by supplying UI to Board object."""

    def __init__(self, board):
        """Initializes a Game object with the given Board object.

        The Board object can be a board in any given status or stage.

        Args:
            board: a Board object to continue (or start) playing.

        Returns:
            None (alters self)

        Raises:
            Nothing (assume board is legal).

        """
        self.board = board

    def get_status(self):
        """Returns the current status of the game.

        The current status of the game is as followed:
            NotStarted: if all cells are hidden.
            InProgress: if some cells are hidden and some are uncovered, and
            no cell with a mine is uncovered.
            Lose: a cell with mine is uncovered.
            Win: All non-mine cells are uncovered, and all mine cells are
            covered.

        Returns:
            one of GameStatus values (doesn't alters self)

        """
        uncovered = self.board.getUncoveredCells()
        if uncovered == []:
            return GameStatus.NotStarted

        rows, columns = self.board.getRows(), self.board.getColumns()

        cells = [(r,c) for r in range(rows) for c in range(columns)]

        Win = True
        for (r,c) in cells:
            if (r,c) in uncovered and self.board.get_value(r, c) == '*':
                return GameStatus.Lose
            if (r,c) not in uncovered and self.board.get_value(r, c) != '*':
                Win = False
        
        if Win:
            return GameStatus.Win

        return GameStatus.InProgress

    def make_move(self, row, column):
        """Makes a move by uncovering the given cell and unrippling it's area.

        The move flow is as following:
        1. Uncover the cell
        2. If the cell is a mine - return
        3. if the cell is not a mine, ripple (if value = 0) and uncover all
            cells according to the ripple sequence, then return

        Args:
            row: row index (integer)
            column: column index (integer)

        Returns:
            the cell's value.

        Raises:
            IllegalMoveException, IllegalIndicesException (generated by Board)

        """
        self.board.uncover(row, column)
        value = self.board.get_value(row, column)
        
        if value != '*':
            sequence = self.board.ripple_sequence(row, column)
            for (r,c) in sequence:
                self.board.uncover(r,c)
        
        return value

    def printMenu(self):
        rows, columns = self.board.getRows(), self.board.getColumns()
        indexing = '  ' + str(range(columns))[1:-1].replace(',', ' ')

        # print the current state of the board
        print indexing
        for r in range(rows):
            line = str(r)
            for c in range(columns):
                line = line + ' '
                if self.board.is_hidden(r, c) == 'H':
                    line += 'H '
                else:
                    line += self.board.get_value(r, c) + ' '
            print line

        # print the game status
        statusEnum = self.get_status()
        status = ''
        if statusEnum == GameStatus.NotStarted:
            status = 'NotStarted'
        elif statusEnum == GameStatus.InProgress:
            status = 'InProgress'
        elif statusEnum == GameStatus.Lose:
            status = 'Lose'
        elif statusEnum == GameStatus.Win:
            status = 'Win'
            
        print 'Game status: %s'%status

        # print the available actions
        availableActions = 'Available actions: (1) Save | (2) Exit | (3) Move'
        if self.get_status() in [GameStatus.Win, GameStatus.Lose]:
            availableActions = 'Available actions: (1) Save | (2) Exit'
        print availableActions

    def run(self):
        """Runs the game loop.

        At each turn, prints the following:
            current state of the board
            game status
            available actions
        And then wait for input and act accordingly.
        More details are in the project's description.

        Returns:
            None

        Raises:
            Nothing

        """

        while True:
            # print board, game status and available options
            self.printMenu()

            # wait for user to select option
            selection = raw_input("Enter selection: ")
            if selection == '1':
                filename = raw_input("Enter filename: ")
                try:
                    self.board.save_board(filename)
                except:
                    print 'Save operation failed'
                else:
                    print 'Save operation done'
            elif selection == '2':
                print 'Goodbye :)'
                return
            elif selection == '3' and self.get_status() not in [GameStatus.Win, GameStatus.Lose]:
                move = raw_input('Enter row then column (space separated): ')
                try:
                    coordinates = move.split()
                    if len(coordinates) != 2:
                        print 'Illegal move values'
                    else:
                        r, c = int(coordinates[0]), int(coordinates[1])
                        self.make_move(r, c)
                except:
                    print 'Illegal move values'
            else:
                print 'Illegal choice'        

def main():
    """Starts the game by parsing the arguments and initializing.

    If an input file argument was given, the file is loaded (even if other
    legal command line argument were given). If any error occurs while parsing
    the input file and creating the board, print "Badly-formatted input file"
    and return (None).

    If input file wasn't given, create a board with the rows/columns/mines
    values given (if legal), and if not print
    "Illegal rows/columns/mines values" and return.
    In case both an input file was given and other parameters, ignore the
    others (if they passes argparse legality check), and use only the input
    file. For example, in case we get "-i sample -r 2 -c a" argparse should
    print an error message, but in case we get "-i sample -r 2 -c 2" just use
    the input file and ignore the rest (even if there are missing parameters).

    All arguments (input file, rows, columns and mines) should be checked by
    argparse and converted to file descriptor (input file) or integers (others)
    by argparse itself, and if an error occurs, like non-existing file or
    non-integer value, argparse should show it's error message without any
    additions. The same goes for illegal options in the command line.

    Returns:
        None

    Raises:
        Nothing

    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--input", type=argparse.FileType('r'))
    parser.add_argument('-r', "--rows", type=int, default=1)
    parser.add_argument('-c', "--columns", type=int, default=2)
    parser.add_argument('-m', "--mines", type=int, default=1)
    args = parser.parse_args()
    
    if args.input != None:
        try:
            source = args.input
            rows = int(source.readline().strip())
            columns = int(source.readline().strip())
            lines = source.readlines()
            board = Board(rows, columns)
            board.load_board(lines)
        except:
            print 'Badly-formatted input file'
            return
    else:
        rows, columns, mines = args.rows, args.columns, args.mines
        board = Board(rows, columns)
        board.put_mines(mines)

    game = Game(board)
    game.run()


if __name__ == '__main__':
    main()

# ADD NO CODE OUTSIDE MAIN() OR OUTSIDE A FUNCTION/CLASS (NO GLOBALS), EXCEPT
# IMPORTS WHICH ARE FINE
