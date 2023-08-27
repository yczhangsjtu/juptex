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




# Set the initial editing and merging states to False
editing = False
merging = False



NON_SELECTED = 0
PART_SELECTED = 1
ALL_SELECTED = 2

SELECT_STATE_COLORS = [(255, 255, 255), (127, 127, 127), (0, 0, 255)]
CELL_CONTENT_BACKGROUND = (220, 220, 220)
CELL_BORDER = (255, 255, 255)
WHOLE_BORDER_SELECTOR_SIZE = 12

def multiple_select_state(lst):
    if all(lst):
        return ALL_SELECTED
    elif any(lst):
        return PART_SELECTED
    else:
        return NON_SELECTED


class Table:
    def __init__(self, cell_width, cell_height):
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.cells = [[Cell(row, col, cell_width, cell_height)
                       for col in range(2)]
                      for row in range(3)]
        self.selected_cells = []

    def get_table_height(self):
        return len(self.cells)

    def get_table_width(self):
        return len(self.cells[0])

    def num_horizontal_borders(self):
        return self.get_table_height() + 1

    def num_vertical_borders(self):
        return self.get_table_width() + 1

    def _vertical_border_selected(self, row, index):
        assert index >= 0 and index <= self.get_table_width(), f"Index out of range, {self.get_table_width()} columns, index {index}"
        return (index > 0 and row[index-1].selected_right_border) or \
               (index < self.get_table_width() and row[index].selected_left_border)

    def _horizontal_border_selected(self, col_index, index):
        assert col_index >= 0 and col_index < self.get_table_width(), f"Index out of range, {self.get_table_width()} columns, index {index}"
        return (index > 0 and self.cells[index-1][col_index].selected_bottom_border) or \
               (index < self.get_table_height() and self.cells[index][col_index].selected_top_border)

    def vertical_borders_selected(self):
        vertical_border_select_state = [NON_SELECTED for i in range(self.get_table_width()+1)]
        for i in range(self.num_vertical_borders()):
            vselect = [self._vertical_border_selected(row, i) for row in self.cells]
            vertical_border_select_state[i] = multiple_select_state(vselect)
        return vertical_border_select_state

    def horizontal_borders_selected(self):
        horizontal_border_select_state = [NON_SELECTED for i in range(self.get_table_height()+1)]
        for i in range(self.num_horizontal_borders()):
            hselect = [self._horizontal_border_selected(j, i) for j in range(self.get_table_width())]
            horizontal_border_select_state[i] = multiple_select_state(hselect)
        return horizontal_border_select_state

    def horizontal_selector_rect(self, index):
        assert index >= 0 and index <= self.get_table_height(), f"Index out of range, {self.get_table_height()} rows, index {index}"
        return (Cell.xshift - WHOLE_BORDER_SELECTOR_SIZE - 8,
                Cell.yshift + index * (self.cell_height + Cell.distance) - (Cell.distance + WHOLE_BORDER_SELECTOR_SIZE)//2,
                WHOLE_BORDER_SELECTOR_SIZE,
                WHOLE_BORDER_SELECTOR_SIZE)

    def vertical_selector_rect(self, index):
        assert index >= 0 and index <= self.get_table_width(), f"Index out of range, {self.get_table_width()} columns, index {index}"
        return (Cell.xshift + index * (self.cell_width + Cell.distance) - (Cell.distance + WHOLE_BORDER_SELECTOR_SIZE)//2,
                Cell.yshift - WHOLE_BORDER_SELECTOR_SIZE - 8,
                WHOLE_BORDER_SELECTOR_SIZE,
                WHOLE_BORDER_SELECTOR_SIZE)

    def cell_region_rect(self):
        return (Cell.xshift-Cell.distance,
                Cell.yshift-Cell.distance,
                self.get_table_width() * (self.cell_width+Cell.distance) + Cell.distance,
                self.get_table_height() * (self.cell_height+Cell.distance) + Cell.distance)

    def draw_border_selectors(self):
        # Draw the border selectors
        horizontal_border_select_state = self.horizontal_borders_selected()
        vertical_border_select_state = self.vertical_borders_selected()
        for i in range(self.get_table_height() + 1):
            pygame.draw.rect(screen, SELECT_STATE_COLORS[horizontal_border_select_state[i]],
                             self.horizontal_selector_rect(i), border_radius=3)
            pygame.draw.rect(screen, (0, 0, 0),
                             self.horizontal_selector_rect(i), width=1, border_radius=3)
        for i in range(self.get_table_width() + 1):
            pygame.draw.rect(screen, SELECT_STATE_COLORS[vertical_border_select_state[i]],
                             self.vertical_selector_rect(i), border_radius=3)
            pygame.draw.rect(screen, (0, 0, 0),
                             self.vertical_selector_rect(i), width=1, border_radius=3)

    def edit_selected_cell(self, event, selected_cell):
        # Update the cell text with the typed character
        if event.unicode.isprintable():
            selected_cell.set_text(selected_cell.text + event.unicode)
        elif event.key == pygame.K_BACKSPACE:
            if len(selected_cell.text) > 0:
                selected_cell.set_text(selected_cell.text[:-1])
    
    def insert_row_at_index(self, index):
        assert index >= 0 and index <= self.get_table_height(), f"Index out of range, {self.get_table_height()} rows, index {index}"
        self.cells.insert(index, [Cell(index, col, self.cell_width, self.cell_height)
                                  for col in range(self.get_table_width())])
        for row in self.cells[index+1:]:
            for cell in row:
                cell.row += 1
    
    def insert_column_at_index(self, index):
        assert index >= 0 and index <= self.get_table_width(), f"Index out of range, {self.get_table_width()} columns, index {index}"
        for row in self.cells:
            row.insert(index, Cell(row[0].row, index, self.cell_width, self.cell_height))
            for cell in row[index+1:]:
                cell.col += 1

    def add_row_at_bottom(self):
        self.insert_row_at_index(self.get_table_height())
    
    def add_row_at_top(self):
        self.insert_row_at_index(0)
    
    def add_column_at_right(self):
        self.insert_column_at_index(self.get_table_width())
    
    def add_column_at_left(self):
        self.insert_column_at_index(0)

    def insert_row_below_selected(self):
        selected_row = self.selected_cells[0].row
        selected_col = self.selected_cells[0].col
        self.insert_row_at_index(selected_row+1)
        self.selected_cells = [self.cells[selected_row+1][selected_col]]

    def insert_row_above_selected(self):
        selected_row = self.selected_cells[0].row
        selected_col = self.selected_cells[0].col
        self.insert_row_at_index(selected_row)
        self.selected_cells = [self.cells[selected_row][selected_col]]
    
    def insert_column_left_selected(self):
        selected_row = self.selected_cells[0].row
        selected_col = self.selected_cells[0].col
        self.insert_column_at_index(selected_col)
        self.selected_cells = [self.cells[selected_row][selected_col]]
    
    def insert_column_right_selected(self):
        selected_row = self.selected_cells[0].row
        selected_col = self.selected_cells[0].col
        self.insert_column_at_index(selected_col+1)
        self.selected_cells = [self.cells[selected_row][selected_col+1]]

    def delete_selected_cells(self):
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            if self.get_table_height() > 1:
                selected_row = self.selected_cells[0].row
                del self.cells[selected_row]
                for row_index, row in enumerate(self.cells):
                    for cell in row:
                        cell.row = row_index
                self.selected_cells = []
                for row in self.cells:
                    for cell in row:
                        cell.unset_selected()
        elif self.get_table_width() > 1:
            selected_col = self.selected_cells[0].col
            for row in self.cells:
                del row[selected_col]
                for col_index, cell in enumerate(row):
                    cell.col = col_index
            self.selected_cells = []
            for row in self.cells:
                for cell in row:
                    cell.unset_selected()

    def export_to_latex(self):
        # Initialize the LaTeX code
        latex = "\\begin{tabular}{|" + "c|" * table.get_table_width() + "}\n"

        # Add the contents of each cell to the LaTeX code
        for row in self.cells:
            for cell in row:
                latex += cell.text + " & "
            latex = latex[:-2] + " \\\\\n"

        # Close the LaTeX table
        latex += "\\end{tabular}"

        return latex
    
    def toggle_row_border(self, i):
        horizontal_border_select_state = self.horizontal_borders_selected()
        if horizontal_border_select_state[i] < ALL_SELECTED:
            if i > 0:
                for cell in table.cells[i-1]:
                    cell.set_selected_bottom_border()
            if i < table.get_table_height():
                for cell in table.cells[i]:
                    cell.set_selected_top_border()
        else:
            if i > 0:
                for cell in table.cells[i-1]:
                    cell.unset_selected_bottom_border()
            if i < table.get_table_height():
                for cell in table.cells[i]:
                    cell.unset_selected_top_border()
    
    def toggle_column_border(self, i):
        vertical_border_select_state = table.vertical_borders_selected()
        if vertical_border_select_state[i] < ALL_SELECTED:
            if i > 0:
                for j in range(table.get_table_height()):
                    table.cells[j][i-1].set_selected_right_border()
            if i < table.get_table_width():
                for j in range(table.get_table_height()):
                    table.cells[j][i].set_selected_left_border()
        else:
            if i > 0:
                for j in range(table.get_table_height()):
                    table.cells[j][i-1].unset_selected_right_border()
            if i < table.get_table_width():
                for j in range(table.get_table_height()):
                    table.cells[j][i].unset_selected_left_border()

def on_press_enter():
    if not table.selected_cells:
        for row in table.cells:
            for cell in row:
                cell.toggle_select_border_and_unselect()
        return

    if table.selected_cells[0].row == table.get_table_height() - 1 and pygame.key.get_mods() == 0:
        table.add_row_at_bottom()

    elif pygame.key.get_mods() & pygame.KMOD_CTRL:
        table.insert_row_below_selected()

    elif pygame.key.get_mods() & pygame.KMOD_SHIFT:
        table.insert_row_above_selected()

    for row in table.cells:
        for cell in row:
            cell.unset_selected()

    table.selected_cells[0].set_selected()


def on_key_down(event):
    global editing, merging
    # Update the cell text if editing
    if editing:
        if table.selected_cells:
            # Get the currently selected cell
            # If multiple selected, only edit the
            # first
            table.edit_selected_cell(event, table.selected_cells[0])
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
        on_press_enter()
    # Stop the cell merging process if "Esc" is pressed
    elif event.key == pygame.K_ESCAPE:
        merging = False
        table.selected_cells.clear()
        for row in table.cells:
            for cell in row:
                cell.unset_selected()
    elif event.key == pygame.K_TAB and table.selected_cells:
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            table.insert_column_left_selected()
        else:
            table.insert_column_right_selected()
    elif event.key == pygame.K_d and table.selected_cells:
        table.delete_selected_cells()


def on_mouse_down(event):
    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Clear the selected cells if the user clicked on an empty space
    table.selected_cells.clear()

    # Check if the user clicked on a cell
    for row in table.cells:
        for cell in row:
            if cell.is_inside(mouse_x, mouse_y):
                # Set the clicked cell as the selected cell
                table.selected_cells.append(cell)
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
    
    # Click on the select-entire-row-border button
    for i in range(table.get_table_height()+1):
        x, y, w, h = table.horizontal_selector_rect(i)
        if x <= mouse_x < x+w and y <= mouse_y < y+h:
            table.toggle_row_border(i)

    # Click on the select-entire-column-border button
    for i in range(table.get_table_width()+1):
        x, y, w, h = table.vertical_selector_rect(i)
        if x <= mouse_x < x+w and y <= mouse_y < y+h:
            table.toggle_column_border(i)

def on_mouse_motion(event):
    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Check if the user is merging cells
    if merging and pygame.mouse.get_pressed()[0]:
        # Add the hovered cell to the selected cells list
        for row in table.cells:
            for cell in row:
                if cell.is_inside(mouse_x, mouse_y) and cell not in table.selected_cells:
                    table.selected_cells.append(cell)
                    cell.set_selected()


cell_width = 80
cell_height = 20

if __name__ == "__main__":
    table = Table(cell_width=80, cell_height=20)

    # Run the game loop
    running = True
    while running:
        for event in pygame.event.get():
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                on_key_down(event)
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                on_mouse_down(event)
            # Handle mouse movement events
            elif event.type == pygame.MOUSEMOTION:
                on_mouse_motion(event)
            # Handle the "Quit" event
            elif event.type == pygame.QUIT:
                running = False

        # Draw the cell background
        pygame.draw.rect(screen, CELL_CONTENT_BACKGROUND, (0, 0, *window_size))
        pygame.draw.rect(screen, CELL_BORDER, table.cell_region_rect())

        # Draw the table
        for row in table.cells:
            for cell in row:
                cell.draw(screen, editing)
        table.draw_border_selectors()

        # Update the display
        pygame.display.flip()