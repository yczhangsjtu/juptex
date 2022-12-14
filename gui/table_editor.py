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


def get_border_select_state():
    vertical_border_select_state = [0 for i in range(len(table[0])+1)]
    horizontal_border_select_state = [0 for i in range(len(table)+1)]
    for i in range(len(table[0])+1):
        vselect = [(i > 0 and row[i-1].selected_right_border) or
                   (i < len(table[0]) and row[i].selected_left_border)
                   for row in table]
        if all(vselect):
            vertical_border_select_state[i] = 2
        elif any(vselect):
            vertical_border_select_state[i] = 1
    for i in range(len(table)+1):
        hselect = [(i > 0 and table[i-1][j].selected_bottom_border) or
                   (i < len(table) and table[i][j].selected_top_border)
                   for j in range(len(table[0]))]
        if all(hselect):
            horizontal_border_select_state[i] = 2
        elif any(hselect):
            horizontal_border_select_state[i] = 1
    horizontal_selector_rect = [(Cell.xshift - 20,
            Cell.yshift + i * (cell_height+Cell.distance) - Cell.distance//2 - 6,
            12, 12) for i in range(len(table)+1)]
    vertical_selector_rect = [(Cell.xshift + i * (cell_width+Cell.distance) - Cell.distance//2 - 6,
                Cell.yshift - 20,
                12, 12) for i in range(len(table[0])+1)]
    return horizontal_border_select_state, vertical_border_select_state, horizontal_selector_rect, vertical_selector_rect


# Create the selected cells list
selected_cells = []

# Set the initial editing and merging states to False
editing = False
merging = False

# Run the game loop
running = True
while running:
    horizontal_border_select_state, vertical_border_select_state, horizontal_selector_rect, vertical_selector_rect = get_border_select_state()
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
            elif event.key == pygame.K_RETURN:
                if selected_cells:
                    if selected_cells[0].row == len(table) - 1 and pygame.key.get_mods() == 0:
                        added_row_index = len(table)
                        selected_col = selected_cells[0].col
                        table.append([Cell(added_row_index, col, cell_width, cell_height) for col in range(len(table[0]))])
                        selected_cells = [table[added_row_index][selected_col]]
                        for row in table:
                            for cell in row:
                                cell.unset_selected()
                        selected_cells[0].set_selected()
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
                else:
                    for row in table:
                        for cell in row:
                            if cell.selected_left_border:
                                cell.left_border = not cell.left_border
                            if cell.selected_right_border:
                                cell.right_border = not cell.right_border
                            if cell.selected_top_border:
                                cell.top_border = not cell.top_border
                            if cell.selected_bottom_border:
                                cell.bottom_border = not cell.bottom_border
                            cell.unset_selected_left_border()
                            cell.unset_selected_right_border()
                            cell.unset_selected_top_border()
                            cell.unset_selected_bottom_border()
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
                    if cell.is_on_left_border(mouse_x, mouse_y):
                        cell.toggle_selected_left_border()
                    elif cell.is_on_right_border(mouse_x, mouse_y):
                        cell.toggle_selected_right_border()
                    elif cell.is_on_top_border(mouse_x, mouse_y):
                        cell.toggle_selected_top_border()
                    elif cell.is_on_bottom_border(mouse_x, mouse_y):
                        cell.toggle_selected_bottom_border()
            
            for i in range(len(table)+1):
                x, y, w, h = horizontal_selector_rect[i]
                if x <= mouse_x < x+w and y <= mouse_y < y+h:
                    if horizontal_border_select_state[i] < 2:
                        if i > 0:
                            for cell in table[i-1]:
                                cell.set_selected_bottom_border()
                        if i < len(table):
                            for cell in table[i]:
                                cell.set_selected_top_border()
                    else:
                        if i > 0:
                            for cell in table[i-1]:
                                cell.unset_selected_bottom_border()
                        if i < len(table):
                            for cell in table[i]:
                                cell.unset_selected_top_border()

            for i in range(len(table[0])+1):
                x, y, w, h = vertical_selector_rect[i]
                if x <= mouse_x < x+w and y <= mouse_y < y+h:
                    if vertical_border_select_state[i] < 2:
                        if i > 0:
                            for j in range(len(table)):
                                table[j][i-1].set_selected_right_border()
                        if i < len(table[0]):
                            for j in range(len(table)):
                                table[j][i].set_selected_left_border()
                    else:
                        if i > 0:
                            for j in range(len(table)):
                                table[j][i-1].unset_selected_right_border()
                        if i < len(table[0]):
                            for j in range(len(table)):
                                table[j][i].unset_selected_left_border()

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
    pygame.draw.rect(screen,
                     (220, 220, 220),
                     (0, 0, *window_size))
    pygame.draw.rect(screen,
                     (255, 255, 255),
                     (Cell.xshift-Cell.distance,
                      Cell.yshift-Cell.distance,
                      len(table[0]) * (cell_width+Cell.distance) + Cell.distance,
                      len(table) * (cell_height+Cell.distance) + Cell.distance))
    # Draw the table
    for row in table:
        for cell in row:
            cell.draw(screen, editing)
    
    # Draw the border selectors
    horizontal_border_select_state, vertical_border_select_state, horizontal_selector_rect, vertical_selector_rect = get_border_select_state()
    for i in range(len(table) + 1):
        pygame.draw.rect(screen,
                         [(255, 255, 255),
                          (127, 127, 127),
                          (0, 0, 255)][horizontal_border_select_state[i]],
                         horizontal_selector_rect[i], border_radius=3)
        pygame.draw.rect(screen, (0, 0, 0),
                         horizontal_selector_rect[i], width=1, border_radius=3)
    for i in range(len(table[0]) + 1):
        pygame.draw.rect(screen,
                         [(255, 255, 255),
                          (127, 127, 127),
                          (0, 0, 255)][vertical_border_select_state[i]],
                         vertical_selector_rect[i], border_radius=3)
        pygame.draw.rect(screen, (0, 0, 0),
                         vertical_selector_rect[i], width=1, border_radius=3)

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
