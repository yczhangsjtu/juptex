import pygame
from juptex.gui.cell import Cell

# Initialize Pygame
pygame.init()

# Set the window size
window_size = (800, 600)

# Create the window
screen = pygame.display.set_mode(window_size)

# Set the window title
pygame.display.set_caption("Table Editor")

# Set the background color
screen.fill((255, 255, 255))
cell_width = 80
cell_height = 20

# Create the table with empty cells
table = [[Cell(row, col, cell_width, cell_height)
          for col in range(2)]
         for row in range(3)]

# Create the selected cells list
selected_cells = []

# Set the initial editing and merging states to False
editing = False
merging = False

# Run the game loop
running = True
while running:
    for event in pygame.event.get():
        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            # Update the cell text if editing
            if editing:
                if selected_cells:
                    # Get the currently selected cell
                    selected_cell = selected_cells[0]

                    # Update the cell text with the typed character
                    if event.unicode.isprintable():
                        selected_cell.set_text(
                            selected_cell.text + event.unicode)
                    elif event.key == pygame.K_BACKSPACE:
                        if len(selected_cell.text) > 0:
                            selected_cell.set_text(selected_cell.text[:-1])

                # Stop the editing if the user presses "Escape"
                if event.key == pygame.K_ESCAPE:
                    editing = False

            # Start the cell merging process if "m" is pressed
            elif event.key == pygame.K_m:
                merging = True
            elif event.key == pygame.K_i:
                editing = True
                merging = False
            elif event.key == pygame.K_RETURN and selected_cells:
                if selected_cells[0].row == len(table) - 1 and pygame.key.get_mods() == 0:
                    added_row_index = len(table)
                    selected_col = selected_cells[0].col
                    table.append([Cell(added_row_index, col, cell_width, cell_height) for col in range(len(table[0]))])
                    selected_cells = [table[added_row_index][selected_col]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    table[added_row_index][selected_col].set_selected()
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                    selected_row = selected_cells[0].row
                    selected_col = selected_cells[0].col
                    table[:] = table[:selected_row+1] + [[Cell(selected_row+1, col, cell_width, cell_height) for col in range(len(table[0]))]] + table[selected_row+1:]
                    for row_index, row in enumerate(table):
                        for cell in row:
                            cell.row = row_index
                    selected_cells = [table[selected_row+1][selected_col]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    selected_cells[0].set_selected()
                elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    selected_row = selected_cells[0].row
                    selected_col = selected_cells[0].col
                    table[:] = table[:selected_row] + [[Cell(selected_row, col, cell_width, cell_height) for col in range(len(table[0]))]] + table[selected_row:]
                    for row_index, row in enumerate(table):
                        for cell in row:
                            cell.row = row_index
                    selected_cells = [table[selected_row][selected_col]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    selected_cells[0].set_selected()
            # Stop the cell merging process if "Esc" is pressed
            elif event.key == pygame.K_ESCAPE:
                merging = False
                selected_cells.clear()
                for row in table:
                    for cell in row:
                        cell.unset_selected()
            elif event.key == pygame.K_TAB and selected_cells:
                if selected_cells[0].col == len(table[0]) - 1 and pygame.key.get_mods() == 0:
                    col = len(table[0])
                    selected_row = selected_cells[0].row
                    for row_index, row in enumerate(table):
                        row.append(Cell(row_index, col, cell_width, cell_height))
                    selected_cells = [table[selected_cells[0].row][col]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    table[selected_row][-1].set_selected()
                elif pygame.key.get_mods() & pygame.KMOD_CTRL:
                    selected_row = selected_cells[0].row
                    selected_col = selected_cells[0].col
                    for row_index, row in enumerate(table):
                        row[:] = row[:selected_col+1] + [Cell(row_index, selected_col+1, cell_width, cell_height)] + row[selected_col+1:]
                        for col_index in range(selected_col+2, len(row)):
                            row[col_index].col = col_index
                    selected_cells = [table[selected_row][selected_col+1]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    selected_cells[0].set_selected()
                elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    selected_row = selected_cells[0].row
                    selected_col = selected_cells[0].col
                    for row_index, row in enumerate(table):
                        row[:] = row[:selected_col] + [Cell(row_index, selected_col, cell_width, cell_height)] + row[selected_col:]
                        for col_index in range(selected_col+1, len(row)):
                            row[col_index].col = col_index
                    selected_cells = [table[selected_row][selected_col]]
                    for row in table:
                        for cell in row:
                            cell.unset_selected()
                    selected_cells[0].set_selected()
            elif event.key == pygame.K_d and selected_cells:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if len(table) > 1:
                        selected_row = selected_cells[0].row
                        del table[selected_row]
                        for row_index, row in enumerate(table):
                            for cell in row:
                                cell.row = row_index
                        selected_cells = []
                        for row in table:
                            for cell in row:
                                cell.unset_selected()
                elif len(table[0]) > 1:
                    selected_col = selected_cells[0].col
                    for row in table:
                        del row[selected_col]
                        for col_index, cell in enumerate(row):
                            cell.col = col_index
                    selected_cells = []
                    for row in table:
                        for cell in row:
                            cell.unset_selected()

        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Clear the selected cells if the user clicked on an empty space
            selected_cells.clear()
            editing = False

            # Check if the user clicked on a cell
            for row in table:
                for cell in row:
                    if cell.is_inside(mouse_x, mouse_y):
                        # Set the clicked cell as the selected cell
                        selected_cells.append(cell)
                        cell.set_selected()
                    else:
                        cell.unset_selected()

        # Handle mouse movement events
        elif event.type == pygame.MOUSEMOTION:
            # Get the mouse position
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if the user is merging cells
            if merging:
                # Add the hovered cell to the selected cells list
                for row in table:
                    for cell in row:
                        if cell.is_inside(mouse_x, mouse_y) and cell not in selected_cells:
                            selected_cells.append(cell)
                            cell.set_selected()

        # Handle the "Quit" event
        elif event.type == pygame.QUIT:
            running = False


    # Draw the cell background
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, *window_size))
    # Draw the table
    for row in table:
        for cell in row:
            cell.draw(screen, editing)

    # Update the display
    pygame.display.flip()


def export_to_latex():
    # Initialize the LaTeX code
    latex = "\\begin{tabular}{|" + "c|"*len(table[0]) + "}\n"

    # Add the contents of each cell to the LaTeX code
    for row in table:
        for cell in row:
            latex += cell.text + " & "
        latex = latex[:-2] + " \\\\\n"

    # Close the LaTeX table
    latex += "\\end{tabular}"

    return latex
