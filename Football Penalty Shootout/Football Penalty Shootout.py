import pygame
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load a sound effect and background music
background_music = 'music1.mp3'
kick_sound=pygame.mixer.Sound('kick.mp3')
collision_sound=pygame.mixer.Sound('collision.mp3')

# Play the background music
#pygame.mixer.music.load(background_music)
#pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely
# Screen setup
win_width = 1000
win_height = 700
win = pygame.display.set_mode((win_width, win_height))
FPS = 60
clock = pygame.time.Clock()

# Load images
background_image = pygame.image.load('background4.jpg')  # Load your background image here
goalpost = pygame.image.load('Terrains.png')
goalpost_height = 250
goalpost_width = 520
footballs = pygame.image.load('zee-ball.png').convert_alpha()
keeper_stand = [
                pygame.image.load('stand-small.png'),
                pygame.image.load('left-save-small.png'),
                pygame.image.load('right-save-small.png'),
                pygame.image.load('top-left-save-small.png'),
                pygame.image.load('top-right-save-small.png'),
                pygame.image.load('top-save-small.png')
               ]


# Define bar coordinates
outer_upper_left_bar = (243, 81)
outer_bottom_left_bar = (243, 330)
outer_upper_right_bar = (765, 81)
outer_bottom_right_bar = (765, 330)

inner_upper_left_bar = (249, 90)
inner_bottom_left_bar = (249, 326)
inner_upper_right_bar = (750, 90)
inner_bottom_right_bar = (750, 326)

#moving_circle
moving_circle_radius = 15
moving_circle_x = 300
moving_circle_y = 300
moving_circle_dx = 8
moving_circle_dy = 0.8

#flags
player_turn=True
is_collides=False
to_restart=False
time_start = False
is_goal=False
is_out=False
time = 1000
space_pressed = False
to_shoot = False
check_for_key=True
pygame.key.set_repeat(0, 0)

#initial position
keeper_initial_x=460
keeper_initial_y=225
ball_initial_x=503
ball_initial_y=606
ball_radius=21
player_score=0
computer_score=0
count=10


def display_menu():
    menu_font = pygame.font.Font(None, 74)
    menu_options = ["PLAY", "INSTRUCTIONS", "EXIT"]
    option_rects = []
    font_color = (255, 255, 255)  # Change this to any color you like (R, G, B)

    while True:
        win.blit(background_image, (0, 0))  # Draw the background image
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(mouse_x, mouse_y):
                        if i == 0:
                            return "PLAY"
                        if i == 1:
                            return "INSTRUCTIONS"
                        if i == 2:
                            pygame.quit()
                            return "EXIT"

        option_rects.clear()
        for i, option in enumerate(menu_options):
            text = menu_font.render(option, True, font_color)  # Set font color here
            rect = text.get_rect(center=(win_width // 2, 200 + i * 100))
            option_rects.append(rect)
            win.blit(text, rect.topleft)

        pygame.display.update()
        clock.tick(FPS)

def display_instructions():
    instruction_font = pygame.font.Font(None, 40)
    instructions = [
        "Instructions:",
        "1. Use the spacebar to move UP the target.",
        "2. Release the spacebar to shoot.",
        "3. Press 'RIGHT' to keep the target in same position.",
        "4. Press 'LEFT' to move the target down.",
        "Press any key to go back to the menu."
    ]
    font_color = (255, 255, 255)  # Change this to any color you like (R, G, B)

    while True:
        win.blit(background_image, (0, 0))  # Draw the background image
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "EXIT"
            if event.type == pygame.KEYDOWN:
                return "MENU"
        
        for i, line in enumerate(instructions):
            text = instruction_font.render(line, True, font_color)  # Set font color here
            win.blit(text, (50, 100 + i * 50))
        
        pygame.display.update()
        clock.tick(FPS)

def display_confirmation():
    confirmation_font = pygame.font.Font(None, 50)
    confirmation_text = "Are you sure you want to return to the main menu?"
    yes_button = Button("YES", (350, 350), None)
    no_button = Button("NO", (550, 350), None)
    font_color = (255, 255, 255)

    while True:
        win.blit(background_image, (0, 0))  # Draw the background image
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.click(event):
                    return "MENU"
                if no_button.click(event):
                    return None

        text = confirmation_font.render(confirmation_text, True, font_color)
        win.blit(text, (100, 250))
        yes_button.show(win)
        no_button.show(win)

        pygame.display.update()
        clock.tick(FPS)


class Button:
    def __init__(self, text, pos, font, bg="black", feedback=""):
        self.x, self.y = pos
        self.font = pygame.font.Font(font, 40)
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg)

    def change_text(self, text, bg="black"):
        self.text = self.font.render(text, True, pygame.Color("White"))
        self.size = self.text.get_size()
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def show(self, win):
        win.blit(self.surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            return True
        return False


#Class for Goalkeeper
class Goalkeeper:
    def __init__(self):
        self.has_landed = False 
        self.keeper_stand=keeper_stand
        self.keeper_x=460
        self.keeper_y=225
        self.initial_y=225
        self.initial_x=460
        self.start_diving=False
        self.start_falling=False
        self.random_save=3
        self.move=random.randint(0,1)
        self.angle=0
        self.rect1=pygame.Rect(self.keeper_x,self.keeper_y,90,139)
        self.rect_surface = pygame.Surface((70, 200),pygame.SRCALPHA)  # Use SRCALPHA for transparency
        self.rectangle_angle=135
        self.rotated_surface = pygame.transform.rotate(self.rect_surface,45)
        self.rotated_rect = self.rotated_surface.get_rect(center=(self.keeper_x+90,self.keeper_y+70))

        self.keeper_vel_x=0
        self.keeper_vel_y=0
        self.gravity=0.5
        self.initial_velocity=0
        self.time=0
        self.save_time=0
        self.tick_time=0
        self.direction=0
        self.opposite=False
        self.check=True
        self.choice=random.randint(0,1)
        self.maximum_height=0
        self.maximum_width=0
    def draw(self,win):
        #win.fill((0,0,0))
       #global rotated_surface,rotated_rect
       if self.start_diving:
            if self.random_save==1 or self.random_save==2:
                self.rect1=pygame.Rect(self.keeper_x,self.keeper_y,180,70)
            elif self.random_save==5:
                self.rect1=pygame.Rect(self.keeper_x+8,self.keeper_y,50,139)
            elif self.random_save==0:
                self.rect1=pygame.Rect(self.keeper_x,self.keeper_y,90,139)
            elif self.random_save==3 or self.random_save==4:
               
                
                if self.random_save==3:
                    self.rectangle_angle=45
                if self.random_save==4:
                   # print('45!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
                    self.rectangle_angle=135


                self.rotated_surface = pygame.transform.rotate(self.rect_surface,self.rectangle_angle)
                self.rotated_rect = self.rotated_surface.get_rect(center=(self.keeper_x+90,self.keeper_y+70))

            else:
                self.rect1=pygame.Rect(self.keeper_x,self.keeper_y,90,139)
       
       pygame.draw.rect(self.rect_surface, (255,0,0), (0, 0, 70, 200))

       
       
       
       #win.blit(self.rotated_surface, self.rotated_rect.topleft)    
       #win.blit(rotated_surface, rotated_rect.topleft)
      # pygame.draw.rect(win,(255,0,0),self.rect1)
       
       if time_start:
            win.blit(self.keeper_stand[self.random_save], (self.keeper_x, self.keeper_y))
       else:
            #pygame.draw.circle(win, (255,255,255), (self.keeper_x, self.keeper_y), 10)
            
            #pygame.draw.rect(win,(255,0,0),(self.keeper_x,self.keeper_y,90,139))
            win.blit(self.keeper_stand[0], (self.keeper_x, self.keeper_y))
    def update(self):
         
         if self.start_diving:
        
           
            if self.random_save!=0:
                if self.check:
                    half_time=self.time/2
                    if self.tick_time>half_time:
                        self.direction=-1
                        
                        self.check=False
                    
                        #print('')
                    else:
                        self.direction=1
            
            
                time_interval=0.5
                self.tick_time+=time_interval
            
                if self.time>self.tick_time:
                    self.keeper_vel_y-=self.gravity*self.direction*time_interval
                    self.keeper_y-=self.keeper_vel_y*self.direction*time_interval 
                
                    if self.random_save==2 or self.random_save==4 or self.random_save==5:
                        if self.random_save==5:
                            if self.choice==0:
                             #   print('self.choice is 0')
                                self.keeper_x=self.keeper_x
                        
                            
                        else:
                            self.keeper_x+=self.keeper_vel_x*time_interval

                    else:
                        self.random_save==1 or self.random_save==3
                        self.keeper_x-=self.keeper_vel_x*time_interval
                else:
                    self.random_save=0   
                 
                    self.has_landed=True
           
           
           
           
            else:
              #  print(self.time,self.tick_time)
                time_interval=0.5
                self.tick_time+=time_interval
                if self.time<self.tick_time:  
                   # print('yes self.time is smaler than tick_time')  
                    self.has_landed=True
                  #  print(self.has_landed)

                else:
                    #print('stop!!!!!!')
                    self.keeper_x=self.initial_x
                    self.keeper_y=self.initial_y

    
    def collision(self,win,football):
           
           # print(self.start_diving)
            if self.start_diving:
                football_rect1=pygame.Rect(football.target_x-football.radius,football.target_y-football.radius,football.radius*2,football.radius*2)
                football_rect=pygame.Rect(football.x-football.radius,football.y-football.radius,football.radius*2,football.radius*2)
               # pygame.draw.rect(win,(0,0,0),football_rect1)
               # pygame.draw.rect(win,(0,0,0),football_rect)
                if self.random_save==0 or self.random_save==1 or self.random_save==2 or self.random_save==5:
                    if self.rect1.colliderect(football_rect) and self.rect1.colliderect(football_rect1) and football.x!=football.target_x and football.y>=320:

                        football.football_collision_with_keeper=True
                        print('collision detected') 
                else:
                    goalkeeper_mask = pygame.mask.from_surface(self.rotated_surface)
                    ball_mask = pygame.mask.from_surface(footballs)

                    offset = (football_rect.left - self.rotated_rect.left,football_rect.top - self.rotated_rect.top)

                    if goalkeeper_mask.overlap(ball_mask, offset) and self.rotated_rect.colliderect(football_rect1) and football.x!=football.target_x and football.y>=320:
                        football.football_collision_with_keeper=True
                        print('collision with top save')
                    #pygame.time.delay(1000)

    def findangle(self):
      #  print('')
        global moving_circle_x,ball_initial_x
        if moving_circle_x>ball_initial_x+85:
            choices=[2,4]
            self.random_save=random.choice(choices)
        elif moving_circle_x<ball_initial_x-85:
            choices=[1,3]
            self.random_save=random.choice(choices)
     
        else:
            choices=[0,5]
            self.random_save=random.choice(choices)
     
        if self.random_save==1 or self.random_save==2 or self.random_save==0:
            self.angle=random.randint(10,35)
            self.initial_velocity=random.randint(8,13)
        elif self.random_save==3 or self.random_save==4 or self.random_save==5:
            self.angle=random.randint(50,80)
            self.initial_velocity=random.randint(10,12)
     

            
    def keeper_motion(self):
     #   print(self.random_save)
        #print(self.angle)
       # print(self.initial_velocity)
        angles=self.angle*math.pi/180

        self.keeper_vel_x=math.cos(angles)*self.initial_velocity
        self.keeper_vel_y=math.sin(angles)*self.initial_velocity
        #self.maximum_height=(self.keeper_vel_y**2)/(2*self.gravity)
       # self.maximum_width=(self.initial_velocity**2)*(math.sin(2*self.angle))/self.gravity       
       # print(self.keeper_x+self.maximum_width)
        self.time=2*self.initial_velocity*math.sin(angles)/self.gravity
        self .save_time=self.time/2
    

# Class for Ball
class Ball:

    def __init__(self, ball_x, ball_y, ball_radius):
        self.x = ball_x
        self.y = ball_y
        self.sound=1
        self.radius = 20
        self.goalpost = goalpost
        self.ball_color = (255, 0, 200)
        self.footballs = footballs
        self.vel_x = 0  # Initial velocity components
        self.vel_y = 0
        self.initial_x = ball_x
        self.initial_y = ball_y
        self.angle = 0
        self.rotate = False
        self.target_x = ball_x
        self.target_y = ball_y
        self.ball_landed=False
        self.speed =random.randint(8,10) # Speed of the ball
        self.is_collide=False
        self.direction_x=0 
        self.direction_y=0
        self.distance1=0
        self.is_collide_left=False
        self.bounce_damping=0.7
        self.count=5
        self.is_collide_right=False
        self.score=0
        self.is_collide_bottom=False
        self.is_collide_up=False
        self.fall_speed=0
        self.ball_falling_position=300
        self.finish=False
        self.football_collision_with_keeper=False
        self.collide_with_keeper=False
        self.scale_factor=1
    def draw(self, win):

        win.fill((255, 255, 255))
        win.blit(self.goalpost, (0, 0))

        # Rotate the ball only if rotate flag is True
        if self.rotate:
            rotated_ball = pygame.transform.rotate(self.footballs, self.angle)
        else:
            rotated_ball = self.footballs

        # Scale the ball based on its distance to the target
        distance = math.hypot(self.target_x - self.initial_x, self.target_y - self.initial_y)
       
        if distance == 0:
            self.scale_factor = 1
        else:
           
            current_distance = math.hypot(self.x - self.initial_x, self.y - self.initial_y)
            self.scale_factor = max(0.9, 0.9)  # Ensure the ball doesn't scale below 20% of its original size
        scaled_ball = pygame.transform.scale(rotated_ball, (int(self.radius * 2 * self.scale_factor), int(self.radius * 2 * self.scale_factor)))
        scaled_rect = scaled_ball.get_rect(center=(self.x, self.y))
    


        win.blit(scaled_ball, scaled_rect)
        

    def update(self):
        global time_start,time,is_goal,is_out

        if not self.is_collide:
            self.direction_x = self.target_x - self.x
            self.direction_y = self.target_y - self.y
           
            self.distance1 = math.hypot(self.direction_x,self.direction_y)
            if self.distance1 != 0:
                self.direction_x /= self.distance1
                self.direction_y /= self.distance1
            

            if self.distance1 < self.speed:
                self.x = self.target_x
                self.y = self.target_y

                
               
               
            else:
                self.x += self.direction_x *self.speed*0.9
                self.y += self.direction_y * self.speed
        

        elif self.collide_with_keeper:
           # print('yes collide with keeper')
          #  self.speed=0    
            #self.rotate=False
            self.rotate=False
            self.x += self.direction_x *self.speed*0.9
            self.y += self.direction_y * self.speed
            #self.ball_landed=True

            
            #print('')

                

        elif self.is_collide_left:
            self.x+=self.direction_x*self.speed
            self.y-=self.direction_x*self.speed
        elif self.is_collide_right:
            self.x+=self.direction_x*self.speed
            self.y+=self.direction_x*self.speed
        elif self.is_collide_up:
            if self.x<500:
                self.x+=self.direction_x*self.speed
                self.y+=self.direction_x*self.speed*2.5   
            else:
                self.x+=self.direction_x*self.speed*2
                self.y-=self.direction_x*self.speed*2   
        else:
            self.x+=self.direction_x*self.speed
            self.y+=self.direction_x*self.speed 

        
       
        if self.x+self.radius<0 or self.x-self.radius>win_width or self.y+self.radius<0 or self.y--self.radius>win_height:
            #pygame.time.wait(1000)
            self.ball_landed=True 


        #bouncing
        

        if time_start and self.y<320: 

            if self.x==self.target_x and self.y==self.target_y:
                if self.x<inner_bottom_right_bar[0] and self.x>inner_bottom_left_bar[0]:
                   
                    is_goal=True
                   
                else:
                    is_out=True
                    is_goal=False
                if self.y==280:
                   self.count+=1
                   self.collide_with_keeper=False
                
                if self.count==50:
                    #print(self.score)
                    self.ball_landed=True
                    if self.x>outer_upper_left_bar[0] and self.x<outer_upper_right_bar[0]:
                        self.score=1
                        print('Goal')

                self.fall_speed+=0.4
                
                self.y+=self.fall_speed
                
                self.target_y=self.y
               
                if self.y + self.radius >self.ball_falling_position :
                    self.y=self.ball_falling_position-self.radius
                   
                    self.fall_speed=-self.fall_speed*self.bounce_damping
                    self.target_y=self.y
                    
            
                
                    
                
                
                
                    

        # Collision with vertical bars
        if (self.x > outer_upper_left_bar[0] and self.x < inner_upper_left_bar[0] and self.y>81 and self.y<330):
             
            print('collision_left')
            self.is_collide_left=True
            self.is_collide=True
        if (self.x   >= inner_upper_right_bar[0] and self.x  <= outer_upper_right_bar[0] and self.y>81 and self.y<330):
            print('collision_right')
            self.is_collide_right=True
            self.is_collide=True


        if (self.y - self.radius <= outer_upper_left_bar[1] and self.y + self.radius >= inner_upper_left_bar[1] and self.x>243 and self.x<765):
            self.is_collide_up=True
            self.is_collide=True
            print('collision up')
        

        global collision_sound
        if self.is_collide and self.sound==1 and not self.collide_with_keeper:
            self.sound=0
            collision_sound.play()
          






        # Update rotation angle only if rotate flag is True
        if self.distance1 != 0:
            if self.rotate:
                if self.x > self.initial_x:
                    self.angle += 5  # Rotate clockwise
                else:
                    self.angle -= 5  # Rotate counter-clockwise





def display_results(win, player_score, computer_score, outcome):
    global count
    # Define colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Define fonts
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    # Create text surfaces
    outcome_text = font.render(outcome, True, black)
    player_score_text = small_font.render(f'Player 1 Score: {player_score}', True, black)
    computer_score_text = small_font.render(f'Player 2 Score: {computer_score}', True, black)
    restart_text = small_font.render('Press R to Restart or Q to Quit', True, black)

    # Get the rectangle of each text surface
    outcome_rect = outcome_text.get_rect(center=(win_width // 2, win_height // 2 - 50))
    player_score_rect = player_score_text.get_rect(center=(win_width // 2, win_height // 2))
    computer_score_rect = computer_score_text.get_rect(center=(win_width // 2, win_height // 2 + 50))
    restart_rect = restart_text.get_rect(center=(win_width // 2, win_height // 2 + 100))

    running=True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Restart the game
                    running = False
                if event.key == pygame.K_q:
                   running=False
                   pygame.quit()
                   
                  


       # global outcome_text,outcome_text,player_score_rect,player
        # Blit the text onto the window
        win.blit(outcome_text, outcome_rect.topleft)
        win.blit(player_score_text, player_score_rect.topleft)
        win.blit(computer_score_text, computer_score_rect.topleft)
        win.blit(restart_text, restart_rect.topleft)

        pygame.display.update()




#scores updating in the screen
# Load font
font = pygame.font.Font(None, 36)  # None uses default font, 36 is font size
status_font=pygame.font.Font(None,80)
# Render text surfaces
player_score_surface = font.render(f'Player 1: {player_score}', True, (255, 255, 255))
computer_score_surface = font.render(f'Player 2: {computer_score}', True, (255, 255, 255))
isgoal=status_font.render(f'Goal!!!!!!!!!', True, (0, 0, 0))
ismissed=status_font.render(f'Missed!!!!!!',True,(0,0,0))


def render_scores():
    # Render text surfaces
    global player_score_surface, computer_score_surface
    player_score_surface = font.render(f'Player 1: {player_score}', True, (255, 255, 255))
    computer_score_surface = font.render(f'Player 2: {computer_score}', True, (255, 255, 255))

def reset_game(football,keeper):
    global player_turn,player_score,computer_score, time_start, to_shoot, moving_circle_x, moving_circle_y, moving_circle_dx, moving_circle_dy, is_collides, space_pressed,ball_radius,ball_initial_x,ball_initial_y,check_for_key,count
    print('Restart')
    
       
    
    score=football.score
    print(score)
    if not player_turn and score==1:
        player_score+=1
    if  player_turn and score==1:
        computer_score+=1
    print(player_score)
    print(computer_score)
    count-=1
     #print(count)
    if count==0:
        print('stop')
        show_results()
        score=0
        player_score=0
        computer_score=0
        count=10
    # Reinitialize football and keeper objects
    football.__init__(ball_initial_x,ball_initial_y,ball_radius)
    keeper.__init__()

    # Reset flags
    time_start = False
    to_shoot = False
    moving_circle_x = 300
    moving_circle_y = 300
    moving_circle_dx = 8
    moving_circle_dy = 0.8
    is_collides = False
    space_pressed = False
    check_for_key=True
    render_scores()

def show_results():
    global win
    if player_score > computer_score:
        outcome = "Player 1 Wins!"
    elif computer_score > player_score:
        outcome = "Player 2 Wins!"
    else:
        outcome = "It's a Draw!"
    
    display_results(win,player_score, computer_score, outcome)













    
def main_game():
    main_menu_button = Button("Main Menu", (10, 80), None,bg="light blue")

    global is_collides,to_restart,to_shoot,space_pressed,is_goal,player_score,player_turn,moving_circle_dx,moving_circle_dy,moving_circle_radius,moving_circle_y,moving_circle_x,time_start,count,check_for_key,is_out
    football = Ball(503, 606, 25)
    keeper=Goalkeeper()
    running=True
    #main_menu_button = Button("Main Menu", (10, 50), None)

    while running:

        keys = pygame.key.get_pressed()
       # print(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame.MOUSEBUTTONDOWN:
                if main_menu_button.click(event):
                    confirm = display_confirmation()
                    if confirm == "MENU":
                        return
                    

            if check_for_key:
                # Check for key presses and releases
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        space_pressed = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_pressed = False
                        to_shoot = True  # Trigger shooting

        if space_pressed:
            moving_circle_y -= moving_circle_dy
            to_shoot = False
        if keys[pygame.K_RIGHT]:
            if moving_circle_y+moving_circle_radius<330:
                moving_circle_y += moving_circle_dy
        if keys[pygame.K_LEFT]:
            if moving_circle_y+moving_circle_radius<330:
                if moving_circle_dy==0:
                    moving_circle_dy=0.8
                moving_circle_y += 2 * moving_circle_dy

        if to_shoot:
            kick_sound.play()
           
            time_start = True
            football.rotate = True  # Start rotating the ball
            football.target_x = moving_circle_x  # Set target position
            football.target_y = moving_circle_y  # Set target position
            moving_circle_dx=0
            moving_circle_dy=0
            keeper.start_diving=True
            keeper.findangle()
            keeper.keeper_motion()
            to_shoot = False
            check_for_key=False
            #print(player_turn)
            player_turn=not player_turn
           # print(player_turn)

        moving_circle_x += moving_circle_dx

        if moving_circle_x + moving_circle_radius >= 850 or moving_circle_x - moving_circle_radius < 150:
            moving_circle_dx = -moving_circle_dx
        if moving_circle_y - moving_circle_radius <70 :
            moving_circle_dy=0
    
        

        football.update()
        keeper.update()
        football.draw(win)
        keeper.draw(win)



        # print(is_collides)
        if  not is_collides:
            keeper.collision(win,football)

        if football.football_collision_with_keeper:
            #print('okay')
            is_collides=True
            football.is_collide=True
            football.collide_with_keeper=True
            football.football_collision_with_keeper=False 

      
       
        if (football.is_collide and not is_goal) or is_out:
            win.blit(ismissed,(380,100))
        if is_goal and not football.is_collide:
            win.blit(isgoal,(380,100))

        if keeper.has_landed and football.ball_landed:
            is_out=False
            reset_game(football,keeper)
            is_goal=False  # Reset the game when the keeper lands
        if not time_start:
            pygame.draw.circle(win, (0, 0, 0), (moving_circle_x, moving_circle_y), moving_circle_radius)
       
        win.blit(player_score_surface, (20, 20))
        win.blit(computer_score_surface, (win_width - computer_score_surface.get_width() - 20, 20))
        main_menu_button.show(win)
        pygame.display.update()
        clock.tick(FPS)

#Start
while True:
    choice = display_menu()
    if choice == "PLAY":
        main_game()
    elif choice == "INSTRUCTIONS":
        display_instructions()
    elif choice == "EXIT":
        break

pygame.quit()
