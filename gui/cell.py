import pygame


class Cell:
    distance = 5
    xshift = 30
    yshift = 25
    def __init__(self, row, col, width, height):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.text = ""
        self.selected = False
        self.merged = False
        self.merge_group = []
        self.top_border = False
        self.left_border = False
        self.right_border = False
        self.bottom_border = False
        self.xshift = Cell.xshift
        self.yshift = Cell.yshift
        self.selected_left_border = False
        self.selected_right_border = False
        self.selected_top_border = False
        self.selected_bottom_border = False
    
    def get_rect(self):
        return (self.col*(self.width + Cell.distance) + self.xshift,
                self.row*(self.height + Cell.distance) + self.yshift,
                self.width, self.height)
    
    def get_top_left(self):
        x, y, w, h = self.get_rect()
        return x, y
    
    def get_bottom_left(self):
        x, y, w, h = self.get_rect()
        return x, y + h
    
    def get_top_right(self):
        x, y, w, h = self.get_rect()
        return x + w, y
    
    def get_bottom_right(self):
        x, y, w, h = self.get_rect()
        return x + w, y + h
        
    def draw(self, screen, editing=False):
        # Draw the cell background
        pygame.draw.rect(screen,
                         (255, 255, 255) if editing and self.selected else (200, 200, 200),
                         self.get_rect())
        
        # Draw the cell borders
        if self.top_border or self.selected_top_border:
            pygame.draw.rect(screen,
                            (0, 0, 255) if self.selected_top_border else (0, 0, 0),
                            (self.get_top_left()[0]-self.distance,
                             self.get_top_left()[1]-self.distance,
                             self.width+self.distance*2,
                             self.distance))
        if self.right_border or self.selected_right_border:
            pygame.draw.rect(screen,
                            (0, 0, 255) if self.selected_right_border else (0, 0, 0),
                            (self.get_top_right()[0],
                             self.get_top_right()[1]-self.distance,
                             self.distance,
                             self.height+self.distance*2))
        if self.bottom_border or self.selected_bottom_border:
            pygame.draw.rect(screen,
                            (0, 0, 255) if self.selected_bottom_border else (0, 0, 0),
                            (self.get_bottom_left()[0]-self.distance,
                             self.get_bottom_left()[1],
                             self.width+self.distance*2,
                             self.distance))
        if self.left_border or self.selected_left_border:
            pygame.draw.rect(screen,
                            (0, 0, 255) if self.selected_left_border else (0, 0, 0),
                            (self.get_top_left()[0]-self.distance,
                             self.get_top_left()[1]-self.distance,
                             self.distance,
                             self.height+self.distance*2))
            
        # Draw the cell text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        # Position the text at the top left corner
        text_rect.topleft = self.get_top_left()[0] + 5, self.get_top_left()[1] + 5
        screen.blit(text_surface, text_rect)
        
        # Draw the cell border
        if self.selected:
            pygame.draw.rect(screen, (255, 0, 0), self.get_rect(), 3)
            
        # Draw the merge group border
        if self.merged:
            pygame.draw.rect(screen,
                             (255, 0, 0),
                             (min([cell.col for cell in self.merge_group])*self.width,
                              min([cell.row for cell in self.merge_group])*self.height,
                              max([cell.col for cell in self.merge_group])*self.width -
                              min([cell.col for cell in self.merge_group])*self.width + self.width,
                              max([cell.row for cell in self.merge_group])*self.height -
                              min([cell.row for cell in self.merge_group])*self.height + self.height),
                             1)
            
    def is_inside(self, x, y):
        x0, y0, w, h = self.get_rect()
        return x0 <= x < x0 + w and y0 <= y < y0 + h
            
    def is_on_left_border(self, x, y):
        x0, y0, w, h = self.get_rect()
        return x0 - self.distance <= x < x0 and y0 - self.distance <= y < y0 + h + self.distance
            
    def is_on_right_border(self, x, y):
        x0, y0, w, h = self.get_rect()
        return x0 + w <= x < x0 + w + self.distance and y0 - self.distance <= y < y0 + h + self.distance
            
    def is_on_bottom_border(self, x, y):
        x0, y0, w, h = self.get_rect()
        return x0 - self.distance <= x < x0 + w + self.distance and y0 + h <= y < y0 + h + self.distance
            
    def is_on_top_border(self, x, y):
        x0, y0, w, h = self.get_rect()
        return x0 - self.distance <= x < x0 + w + self.distance and y0 - self.distance <= y < y0
    
    def set_selected(self):
        self.selected = True
    
    def unset_selected(self):
        self.selected = False
    
    def set_selected_left_border(self):
        self.selected_left_border = True
    
    def toggle_selected_left_border(self):
        self.selected_left_border = not self.selected_left_border
    
    def unset_selected_left_border(self):
        self.selected_left_border = False
    
    def set_selected_right_border(self):
        self.selected_right_border = True
    
    def toggle_selected_right_border(self):
        self.selected_right_border = not self.selected_right_border
    
    def unset_selected_right_border(self):
        self.selected_right_border = False
    
    def set_selected_top_border(self):
        self.selected_top_border = True
    
    def toggle_selected_top_border(self):
        self.selected_top_border = not self.selected_top_border
    
    def unset_selected_top_border(self):
        self.selected_top_border = False
    
    def set_selected_bottom_border(self):
        self.selected_bottom_border = True
    
    def toggle_selected_bottom_border(self):
        self.selected_bottom_border = not self.selected_bottom_border
    
    def unset_selected_bottom_border(self):
        self.selected_bottom_border = False
        
    def set_merged(self, merge_group):
        self.merged = True
        self.merge_group = merge_group
        
    def set_text(self, text):
        self.text = text

    def toggle_select_border_and_unselect(self):
        if self.selected_left_border:
            self.left_border = not self.left_border
        if self.selected_right_border:
            self.right_border = not self.right_border
        if self.selected_top_border:
            self.top_border = not self.top_border
        if self.selected_bottom_border:
            self.bottom_border = not self.bottom_border
        self.unset_selected_left_border()
        self.unset_selected_right_border()
        self.unset_selected_top_border()
        self.unset_selected_bottom_border()