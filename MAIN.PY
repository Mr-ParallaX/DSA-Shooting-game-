import tkinter as tk
from PIL import Image, ImageTk
import random

# Window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Stack & Combo Constants
STACK_LIMIT = 10
COMBO_SIZE = 3

# Enemy types
ENEMY_TYPES = ["Scizor", "Magneton", "Voltorb", "Gloom"]

# Load image assets
def load_image(path, size):
    img = Image.open(path)
    return ImageTk.PhotoImage(img.resize(size, Image.Resampling.LANCZOS))


# Game class
class ShootingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("DSA Combo Shooting Game")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    # Draw vertical glass-like stack container on left side
        self.canvas.pack()

        # Background image if any
        # self.bg = self.canvas.create_image(0, 0, anchor='nw', image=self.bg_img)





        # Load images
        self.bg_img = load_image("background.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.player_img = load_image("player.png", (60, 60))
        self.bullet_img = load_image("bullet.png", (10, 20))
        self.enemy_imgs = {
            "Scizor": load_image("enemy1.png", (40, 40)),
            "Magneton": load_image("enemy2.png", (40, 40)),
            "Voltorb": load_image("enemy3.png", (40, 40)),
            "Gloom": load_image("enemy4.png", (40, 40))
        }

        

        # Draw background
        self.canvas.create_image(0, 0, image=self.bg_img, anchor=tk.NW)
        #vertical left stack border 
        self.stack_border = self.canvas.create_rectangle(
        10, 75, 50, 530,  # (x1, y1, x2, y2)
        # outline="Scizor",
        width=3,
        outline="grey", fill="gray90"

        
        )

        # self.stack_border = self.canvas.create_rectangle(
        # 150, 30, 50, 80,  # (x1, y1, x2, y2)
        # # outline="Scizor",
        # width=3,
        # outline="grey", fill="gray90"

        
        # )


        # Game variables
        self.player = self.canvas.create_image(WINDOW_WIDTH//2, WINDOW_HEIGHT-60, image=self.player_img)
        self.bullets = []
        self.enemies = []
        self.vertical_stack = []
        self.combo_stack = []
        self.score = 0
        self.game_over = False



        # Stack display frame
        self.stack_rects = []
        self.combo_rects = []

        # Bindings
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<space>", self.shoot)

        # Start game
        self.spawn_enemy()
        self.update_game()

    # Move player
    def move_left(self, event):
        if self.canvas.coords(self.player)[0] > 30:
            self.canvas.move(self.player, -20, 0)

    def move_right(self, event):
        if self.canvas.coords(self.player)[0] < WINDOW_WIDTH - 30:
            self.canvas.move(self.player, 20, 0)

    def shoot(self, event):
        x, y = self.canvas.coords(self.player)
        bullet = self.canvas.create_image(x, y - 30, image=self.bullet_img)
        self.bullets.append(bullet)

    # Spawn enemies
    def spawn_enemy(self):
        if self.game_over:
            return
        enemy_type = random.choice(ENEMY_TYPES)
        x = random.randint(50, WINDOW_WIDTH - 50)
        enemy = self.canvas.create_image(x, 0, image=self.enemy_imgs[enemy_type])
        self.enemies.append((enemy, enemy_type))
        self.root.after(2000, self.spawn_enemy)

    # Game loop
    def update_game(self):
        if self.game_over:
            return

        # Move bullets
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -15)
            if self.canvas.coords(bullet)[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # Move enemies
        for enemy, etype in self.enemies[:]:
            self.canvas.move(enemy, 0, 5)
            ex, ey = self.canvas.coords(enemy)
            px, py = self.canvas.coords(self.player)

            # Collision with player
            if abs(px - ex) < 40 and abs(py - ey) < 40:
                self.end_game()
                return

            # Enemy reached bottom
            if ey > WINDOW_HEIGHT:
                
                self.canvas.delete(enemy)
                self.enemies.remove((enemy, etype))

        # Check bullet-enemy collision
        for bullet in self.bullets[:]:
            bx, by = self.canvas.coords(bullet)
            for enemy, etype in self.enemies[:]:
                ex, ey = self.canvas.coords(enemy)
                if abs(bx - ex) < 30 and abs(by - ey) < 30:
                    self.add_to_stack(etype)
                    self.canvas.delete(bullet)
                    self.bullets.remove(bullet)
                    self.canvas.delete(enemy)
                    self.enemies.remove((enemy, etype))
                    break

        self.root.after(50, self.update_game)

    # Stack logic
    def add_to_stack(self, etype):
        if len(self.vertical_stack) >= STACK_LIMIT:
            self.end_game()
            return

        self.vertical_stack.append(etype)
        self.update_stack_display()

        # Check for combo
        if len(self.vertical_stack) >= COMBO_SIZE:
            last_three = self.vertical_stack[-3:]
            if last_three.count(last_three[0]) == 3:
                self.vertical_stack = self.vertical_stack[:-3]
                self.combo_stack.append(last_three[0])
                self.score += 1
                self.update_stack_display()
                self.update_combo_display()

    # Draw vertical stack
    def update_stack_display(self):
        for rect in self.stack_rects:
            self.canvas.delete(rect)
        self.stack_rects = []

        x = 30
        y = 100
        for etype in self.vertical_stack:
            img = self.enemy_imgs[etype]
            rect = self.canvas.create_image(x, y, image=img)
            self.stack_rects.append(rect)
            y += 45
    #draw vertical combo  stack 
    def update_combo_display(self):
    # Delete previous combo stack images
        for rect in self.combo_rects:
            self.canvas.delete(rect)
        self.combo_rects = []

    # Delete previous combo text if exists
        if hasattr(self, 'combo_text_id'):
            self.canvas.delete(self.combo_text_id)

        # Position for combo stack on right side
        x = WINDOW_WIDTH - 50  # X-coordinate on the right
        y = 100  # Start Y

        # Draw each element in the combo stack
        for etype in self.combo_stack:
            img = self.enemy_imgs[etype]
            rect = self.canvas.create_image(x, y, image=img)
            self.combo_rects.append(rect)
            y += 45  # Go down for next

    # Draw a border rectangle around combo stack (optional)
        if self.combo_stack:
            self.canvas.create_rectangle(
                x - 25, 78,
                x + 25, 70 + len(self.combo_stack) * 45,
                outline="white", width=2
            )

    # Draw the "Combo Points" text above the combo stack
        self.combo_text_id = self.canvas.create_text(
            x, 70,  # position above the combo stack
            text=f"Combo Points: {len(self.combo_stack)}",
            fill="white",
            font=("Arial", 8, "bold")
        )








        


    # End game
    def end_game(self):
        self.game_over = True
        popup = tk.Toplevel()
        popup.title("Game Over")
        popup.minsize(300,150)
        popup.maxsize(500,150)
        popup.wm_iconbitmap("22.ico")
        # Load and place background image
        bg_image = ImageTk.PhotoImage(Image.open("gameover_bg.png").resize((300, 150)))
        bg_label = tk.Label(popup, image=bg_image)
        bg_label.image = bg_image  # Keep a reference!
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)


        # self.bg_img = load_image("gameover_bn.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
        tk.Label(popup, text=f"Game Over! Score: {self.score}", font=("Arial", 14)).pack(pady=20)
        tk.Button(popup, text="Restart", command=self.restart_game).pack()

        # Show combo stack
        combo_string = ', '.join(self.combo_stack) if self.combo_stack else "No combo collected"
        tk.Label(popup, text=f"Combo Stack: [{combo_string}]", font=("Arial", 10), bg="black", fg="cyan").pack(pady=10)
        # tk.Label(popup, text=f"Combo Stack: [{len(self.combo_stack)}]", font=("Arial", 10), bg="black", fg="cyan").pack(pady=10)





    # Restart logic
    def restart_game(self):
        self.root.destroy()
        main()  # restart the game


# Launch game
def main():
    root = tk.Tk()
    # to change the icon of the tkinter 
    root.wm_iconbitmap("22.ico")
    root.minsize(800,600)
    root.maxsize(800,600)
    game = ShootingGame(root)
    root.mainloop()

      # game starting window
def show_start_window():
    # Load images
    

    start_window = tk.Tk()
    start_window.title("Welcome to the Game")
    start_window.minsize(500,300)
    start_window.maxsize(500,300)
    # start_window.geometry("500x300")
    start_window.wm_iconbitmap("22.ico")

    # Load background image and resize to match window size
    bg_image = Image.open("gamestart_bg.png").resize((500, 300))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Keep a reference to prevent garbage collection
    start_window.bg_photo = bg_photo

    # Create canvas and add image
    canvas = tk.Canvas(start_window, width=500, height=300)
    canvas.pack()
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)

    # Add welcome text ON the image
    canvas.create_text(250, 110, text="Welcome to the DSA Shooting Game!", font=("Arial", 14, "bold"), fill="white")

    # Add Start button ON the image
    start_button = tk.Button(start_window, text="Start Game", font=("Arial", 10), command=lambda: start_game(start_window))
    canvas.create_window(260, 160, window=start_button)

    start_window.mainloop()
def start_game(start_window):
    start_window.destroy()  # Close the start window
    main()  # Launch your main game logic



        # Entry point of your program
if __name__ == "__main__":
    show_start_window()  #  Launch the start window FIRST







