import cv2
import numpy as np
import os
from solve import solve_constraints, backtrack
import sys
from word2number import w2n



# Backtracking exceeds default recursion depth of 1000
# Testing has runs as high as 10 000+
# Might be better methods than arbitrarily setting to 50 000
sys.setrecursionlimit(50000)

# Use notes as you would when solving puzzle by hand
# 9 x 9 array where each element is an array containing all numbers between 1 and 9 that don't violate the basic rules of sudoku
NOTES = np.zeros((9, 9), object)


##################################
# OPEN PUZZLE AND IMPORT TEMPLATES
##################################

# Convert puzzle to grayscale for template matching
# Keep a colored copy to display final solution
# By default puzzles from sudoku.com are too large to view in window. Scale by 50%
puzzle = cv2.imread("C:/Users/Jacob de Graaf/Documents/python/Final Project/puzzle/puzzle.png", 1)
puzzle = cv2.resize(puzzle, (0, 0), fx = 0.5, fy = 0.5)
gray = cv2.cvtColor(puzzle, cv2.COLOR_BGR2GRAY)

# Screenshots of numbers from sudoku.com used for template matching
# Using the asset file directory allows for sizing and grayscale conversion of all template images
# Store template images in a dictionary -> can use key to print the number that was a match
numbers = {}

for file in os.listdir('C:/Users/Jacob de Graaf/Documents/python/Final Project/assets'):
        # Key is filename without the extension (eg. eight.png saved as 'eight')
        key = os.path.splitext(file)[0]

        img = cv2.imread(os.path.join('C:/Users/Jacob de Graaf/Documents/python/Final Project/assets', file), 0)
        resized = cv2.resize(img, (0,0), fx = 0.5, fy = 0.5)
        numbers[key] = resized


#############################################################
# DEFINE COORIDINATES OF INDIVIDUAL SQUARES WITHIN 9 x 9 GRID
#############################################################

# Use grayscale image, NOT colored copy
# cv2.threshold to convert to binary image (pixels assigned values of 0 or 255)
# Find contours using binary image
# Find squares using approx.PolyDP; squares can be approximated with 4 vertices


# Any pixel with a value > than 200 will be displayed as 255.
ret, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

# Contours is a list of all contours in the image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Square coordiantes must be accesible for template matching and displaying results 
# squares[i] is an array containing the results of boundingRect()
squares = []

# Reverse contours so results generated from top left, not bottom right
for cnt in reversed(contours):
    approx = cv2.approxPolyDP(cnt, 1, True)
    if len(approx) == 4:
        # Some numbers (specifically inside of 4) are being approximated with 4 vertices
        # Only squares will have a width to height ratio of 1:1 (theoretically, use 0.95 for wiggle room)
        x, y, w, h = cv2.boundingRect(cnt)
        if w > h:
            ratio = h / w
        else:
            ratio = w / h

        if ratio >= 0.95:            
            # Store coordinates in squares array
            squares.append([x, y, w, h])


###################
# TEMPLATE MATCHING
###################

# Using the coordinates from squares[] perform template matching against each image stores in numbers{}
# When match occurs, the key for the matching value denotes the number in that square of the puzzle
# Store puzzle information in a 9 x 9 array where grid[i] is a row and grid[i][j] is a square within that row
grid = np.zeros((9, 9), int)
keys = list(numbers.keys())

# Use filled to record which numbers were given in the puzzle -> not used till printing solutions at end of program
filled = np.empty(81)
for i in range(81):
    filled[i] = False


# Threshold for matching found using trial an error. 0.93 works best here.
threshold = 0.93

# Iterate through all 81 squares
for i in range(len(squares)):
    # Array slicing
    # Use coordinates from squares[i] to define target region from puzzle for template matching
    x, y, w, h = squares[i][0], squares[i][1], squares[i][2], squares[i][3]
    target = gray[y:y+h, x:x+w]

    # Check contents of square against all number templates
    for key in keys:
        # matchTemplate returns matrix denoting the similarity between pixels at each location
        result = cv2.matchTemplate(target, numbers[key], cv2.TM_CCOEFF_NORMED)
        (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

        if maxVal > threshold:
            # Squares is a 1 x 81 array, grid is 9 x 9. Basic conversion to input result of template matching into corresponding grid location
            k = i % 9
            j = 0

            if i >= 9:
                j = (i - k) // 9

            # Reminder that key is the file name ('one', 'two', etc). Convert to int to store in grid
            grid[j][k] = int(w2n.word_to_num(key))
            filled[i] = True
            break

     
#######
# SOLVE
#######

solve_constraints(grid)

# Back tracking only required for squares that have not been solved (= 0) after contrainst propagation
# unsolved[] contains coordinates of all squares that are unsolved
# This will make it easier to access the last square which was updated in the the backtracking function
unsolved = []
for i in range(9):
    for j in range(9):
        if grid[i][j] == 0:
            unsolved.append((i, j))

if len(unsolved) > 0:
    backtrack(unsolved, 0, grid) 
           
##################
# DISPLAY SOLUTION
##################

for i in range(9):
    for j in range(9):
        # Need coordinates of individual squares for putText
        square = i * 9 + j
        # Don't show numbers that were in the puzzle to begin with
        if filled[square] == False:
            cv2.putText(puzzle, str(grid[i][j]), (squares[square][0] + 25, squares[square][1] + 75), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 3, cv2.LINE_AA)
cv2.imshow('Solution', puzzle)
cv2.waitKey(0)
cv2.destroyAllWindows