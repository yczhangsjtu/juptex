import pygame


class Cell:
    def __init__(self, row, col, width, height):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.text = ""
        self.selected = False
        self.merged = False
        self.merge_group = []
        
    def draw(self, screen, editing=False):
        # Draw the cell background
        pygame.draw.rect(screen,
                         (255, 255, 255) if editing and self.selected else (200, 200, 200),
                         (self.col*self.width, self.row*self.height, self.width, self.height))
        
        # Draw the cell text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (self.col*self.width + 5, self.row*self.height + 5)  # Position the text at the top left corner
        screen.blit(text_surface, text_rect)
        
        # Draw the cell border
        if self.selected:
            pygame.draw.rect(screen, (255, 255, 0), (self.col*self.width, self.row*self.height, self.width, self.height), 1)
        else:
            pygame.draw.rect(screen, (0, 0, 0), (self.col*self.width, self.row*self.height, self.width, self.height), 1)
            
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
        return self.col*self.width <= x < (self.col+1)*self.width and self.row*self.height <= y < (self.row+1)*self.height
    
    def set_selected(self):
        self.selected = True
    
    def unset_selected(self):
        self.selected = False
        
    def set_merged(self, merge_group):
        self.merged = True
        self.merge_group = merge_group
        
    def set_text(self, text):
        self.text = text
