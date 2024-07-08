# SUDOKU SOLVER
## Video Demo: https://www.youtube.com/watch?v=S5L-79Gw2gQ
## Description:

### Introduction

This project uses OpenCV to view an image of a sudoku puzzle saved to the users computer, and output the solution overlayed on the submitted image.

### Reading the puzzle and other assets
The reading and manipulation of all images is done using functions from the OpenCV library. Take note of the file path that has been provided for each call of the cv2.imread() function; importantly, the puzzle the user wishes to solve must be saved as "puzzle.png". All number images used for template matching must be stored in the subfolder named "assets". Note that the names of the template files correspond to the number depicted in the image ("one.png", "two.png", etc). These file names (minus the .png extension) become keys in the dictionary 'numbers'. The values for each key are the numpy arrays containing the pixel information returned when imread() is called. I found that this dictionary approach was the best way to perform template matching against multiple numbers as you can simply template match against each dictionary entry by using a for loop to iterate through the dictionary keys. More on this later.  

All assets including the puzzle image are resized by 50% (for puzzle.png this is so that the puzzle fits the output window, assets must be scaled the same for template matching to work) and converted to grayscale, a requirement for the cv2.matchTemplate function. A colored copy of the puzzle image is retained in order to display the final solution.

### Defining the sudoku grid
My approach to reading the submitted puzzle was to template match against each of the 81 squares in the puzzle, determining which number, if any, they contained. To do this, I first needed the coordinates that defined each unique square in the puzzle. There were several steps to this process, which were reccomended in the OpenCV documentation:

    1. The grayscale puzzle image was converted to a binary image using cv2.threshold()
    2. A list of contours was generated using cv2.findContours() on the binary image
    3. Each contour within this list was then approximated using cv2.approxPolyDP(). The contour of a square can be approximated using 4 points
    4. Using cv2.boundingRect() on valid contours, I was able to get the x, y, w, and h coordinates of each square in the grid, where x and y define a squares top left corner, and w and h define the width and height of the square from this point.
    5. The results were stored in squares[], which contained 81 elements, each an arrays containing the x, y, w, h information for a single square


### Template matching
With the squares of the puzzle now defined and the number assets storesd in the numbers dictionary, determining which numbers were in the puzzle was as simple as stepping through the squares array and for each square:
    - 'Selecting' the square from the grayscale puzzle image using array slicing and the squares x, y, w, h values
    - Calling matchTemplate against the target square, comparing the pixel values against those of the template images (stored in numbers{})
    - If a match was found, I needed to record which number had been a match. English spelling of numbers ('one', 'two', etc) was of no use for algorithmic solving so I used word2number to change these to their appropriate integers.
    
The results of the template matching were stored in a 9x9 2-Dimensional array called 'grid' where grid[i] represented a row of the puzzle, and grid[i][j] was a square within that row. In doing so, after template matching was complete, grid was essentially a copy of the submitted puzzle that could be understood by the computer and submitted to solving algorithms.

IMPORTANT NOTES: 
- The templateMatching method as well as the threshold for a match of 0.93 were perfected using trial and error. Similarities between the structure of 8 and 3 gave the most difficulty.
- The matchTemplate() function looks for near identical matches between the template and the image it is being given. As a result, this program only works for puzzles that were taken from sudoku.com since this is where I gathered the images of numbers that are used in the matching process.

### Solving the puzzle
Once the puzzle was represented digitally within 'grid', solving the puzzle was done using a combination of constraint propagation and backtracking algorithms. Both of these functions are defined in solve.py and are imported at the beginning of sudoku.py.

solve_constraints is a recursive function which solves naked and hidden singles. A naked single exists there is only one possible solution for any given square. Similarly, a hidden single exists where a given square may have multiple number candidates but one of these numbers does not fit anywhere else in the row, column, or 3x3 to which square n belongs. 

The solve_constraints function is dependent on the global array NOTES, a 9x9 array (like grid) where each element is an array containing all numbers that could be a candidate for that square. For example, if the top left square of the puzzle (grid[0][0]) could accomodate 3, 4, or 9 then NOTES[0][0] = [3, 4, 9]

Once all hidden and naked singles have been updated in grid, NOTES is reset and the process is repeated. For easier puzzles the solution can be derived using this function alone. Unsolved squares contain 0, if a 0 is found during solve_constraints, the variable 'solved' is set to False. Therefore if no zeros are found, solved remains True and the program prints the solution.

More complex problems cannot be solved with this method alone. To complete the puzzle once constraint propagation was exhausted, I used backtracking. By storing all yet-to-be-solved squares in unsolved[] I could then:
- Update square n with the first number that didn't violate the row, column, 3x3 repeat rule
- Progress to square n + 1, and do the same
    - If no number can fill square n + 1, a mistake has been made. Backtrack to square n and update to next valid number.
    - If no other number valid for square n, backtrack to square n - 1, and so on

This was repeated until a number was entered into all unsolved squares. 

Once the puzzle is solved, the solution is read from the 'grid' array, and the answer is displayed using the same coordinates that were originally used to identify each square within the puzzle.

## Final thoughts/comments
I believe that there are more elegant ways to solve the harder problems than by using backtracking to brute force a solution. In my research however, I believe that such methods may require a deeper understanding of how one solves expert level puzzles without the aid of computers. This is something I did not have, and since I was more interested in the coding, I chose brute force.

I am also unsure whether manually raising the max recursion depth from 1000 to 10 000 is ill advised. This is really just an arbitrary value that I have not exceeded during testing so far.

At some point I may explore using better number recognition so that users can upload puzzles from anywhere, not just sudoku.com, but for now I found this to be challenging anough.

Thanks!





