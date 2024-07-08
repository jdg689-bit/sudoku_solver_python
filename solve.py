import numpy as np
import sys
RED = "\033[1;31m"
RESET = "\033[0m"
###################
# SOLVING ALGORITHM
###################

# Solving is a combination of CONSTRAINT PROPAGATION and BACKTRACKING once the former no longer yields results

###########################
# 1. CONSTRAINT PROPAGATION
###########################

def solve_constraints(grid):
    ##################
    # FILL NOTES ARRAY
    ##################

    # Each call of the function wipes NOTES and refills based on updated grid
    # May be better to remove elements of notes where numbers are no longer valid instead
    NOTES = np.zeros((9, 9), object)
    # Track [i][j] positions of updated numbers. Used to print changes in red for testing as well as determining when no further updates have been made (constraint propagation exhausted)
    # Updated used for testing/demonstration only. Allows for printing of updated numbers in different color
    updated = []
    possible = []
    # Set solved to True by default
    solved = True

    for i in range(9):
        for j in range(9):
            # Notes only needed if square is empty
            if grid[i][j] == 0:
                # If grid contains empty squares (0), puzzle is not solved, set to False
                solved = False

                # Define row, column, and 3x3 which current square belongs to
                row = grid[i]

                column = []
                for k in range(9):
                    column.append(grid[k][j])

                # Squares comprising 3x3 are the same for any square with the same top left corner
                box = []
                top_row = (i // 3) * 3
                left_column = (j // 3) * 3

                for row_count in range(3):
                    for column_count in range(3):
                        box.append(grid[top_row + row_count][left_column + column_count])

                # No number can be repeated in a row, column, or 3x3
                # If placing a number in the current square does not violate any of these rules, that number is a possible candidate to fill the square
                possible = []
                for number in range(1, 10):
                    if number not in row and number not in column and number not in box:
                        possible.append(number)

                # Store results in notes
                NOTES[i][j] = possible
    
    #############################################
    # USE NOTES TO SOLVE NAKED AND HIDDEN SINGLES
    #############################################

    for i in range(9):
        for j in range(9):
            # NAKED SINGLES
            # NOTES[i][j] contains only one number -> no other possible solutions for that square
            # Update grid[i][j] with number
            if NOTES [i][j] != 0:
                if (len(NOTES[i][j])) == 1:
                    updated.append((i, j))
                    grid[i][j] = NOTES[i][j][0]

                # HIDDEN SINGLES
                # Within the possible numbers for a given square, a number is NOT VALID for any other squares in the current row, column, or 3x3?
                # Don't include possibilities for current square when determining possible numbers for row, column, or 3x3
                else:
                    row = np.array(0)
                    for square in range(9):
                        if square != j:
                            row = np.append(row, NOTES[i][j])

                    column = np.array(0)
                    for square in range(9):
                        if square != i:
                            column = np.append(column, NOTES[i][j])

                    box = np.array(0)
                    top_row = (i // 3) * 3
                    left_column = (j // 3) * 3

                    for row_count in range(3):
                        for column_count in range(3):
                            if top_row + row_count != i or left_column + column_count != j:
                                box = np.append(box, (NOTES[top_row + row_count][left_column + column_count]))

                    # If number not found in possible numbers for other squares in row, colum, or 3x3, update grid[i][j] with number
                    for number in range(len(NOTES[i][j])):                       
                        if NOTES[i][j][number] not in box or NOTES[i][j][number] not in row or NOTES[i][j][number] not in column:
                            updated.append((i, j))
                            grid[i][j] = NOTES[i][j][number]


    
    print(f'Updated {len(updated)} squares')

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (i, j) in updated:
                sys.stdout.write(f"{RED}{grid[i][j]}{RESET} ")
            else:
                sys.stdout.write(f"{grid[i][j]} ")

        sys.stdout.write("\n")

    print("\n")
    
    
    # Inform user puzzle is solved if that is the case
    if solved:
        return 1
    
    # If no changes made to grid, constraint propagation no longer yielding results
    # Return grid for backtracking
    if len(updated) == 0:
        return(grid)

    # If changes were made to grid, solve for HIDDEN and NAKED SINGLES again using updated grid
    else:
        solve_constraints(grid)


#################
# 2. BACKTRACKING
#################


# ONCE CONSTRAINT PROPAGATION APPROACH HAS FAILED, USE BACKTRACKING TO SOLVE THE REST OF THE PUZZLE
def backtrack(unsolved, index, grid):

    # Get grid coordinates of square using unsolved[]
    i = unsolved[index][0]
    j = unsolved[index][1]

    # Define row, column, 3x3
    row = grid[i]

    column = []
    for k in range(9):
        column.append(grid[k][j])

    box = []
    top_row = (i // 3) * 3
    left_column = (j // 3) * 3

    for row_count in range(3):
        for column_count in range(3):
            box.append(grid[top_row + row_count][left_column + column_count])

    updated = False
    

    # Iterate through numbers 1 - 9, update grid[i][j] with first number that doesn't violate row, column, 3x3 rule 
    for number in range(grid[i][j] + 1, 10):
        if number not in row and number not in column and number not in box:
            grid[i][j] = number
            updated = True
            # Current square now contains a valid (for now) number, proceed to next square
            index = index + 1


            # If solved square was the last square in the unsolved array, the puzzle is solved
            if index == len(unsolved):
                return 1
            
            # Else attempt to solve next square
            else:
                backtrack(unsolved, index, grid)

            

    # If square not updated, need to revisit previous square and try new number
    # Resest current square to 0
    if updated == False:
        grid[i][j] = 0
        index = index - 1

        backtrack(unsolved, index, grid)