import random
import math

class Particle:
    def __init__(self, canvas, x, y, color, size, speed_x, speed_y, life):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.life = life
        self.max_life = life
        self.id = None

    def draw(self):
        alpha_ratio = self.life / self.max_life
        r = int((1 - alpha_ratio) * 255 + alpha_ratio * int(self.color[1:3], 16))
        g = int((1 - alpha_ratio) * 255 + alpha_ratio * int(self.color[3:5], 16))
        b = int((1 - alpha_ratio) * 255 + alpha_ratio * int(self.color[5:7], 16))
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.id = self.canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=color, outline=""
        )

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.speed_y += 0.1  
        self.size *= 0.98
        return self.life > 0

    def remove(self):
        if self.id:
            self.canvas.delete(self.id)

class EffectsManager:
    def __init__(self, canvas, root, sw, sh):
        self.canvas = canvas
        self.root = root
        self.sw = sw
        self.sh = sh
        self.particles = []
        self.running = True
        self.effects = []

    def create_particles(self, x, y, count=20, color="#ff8906", spread=360, speed=2):
        for _ in range(count):
            angle = random.uniform(0, spread) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(0.5, speed)
            speed_y = math.sin(angle) * random.uniform(0.5, speed)
            size = random.uniform(2, 6)
            life = random.randint(30, 60)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_floating_particles(self, count=30, color="#ffffff"):
        for _ in range(count):
            x = random.randint(0, self.sw)
            y = random.randint(0, self.sh)
            speed_x = random.uniform(-0.5, 0.5)
            speed_y = random.uniform(-0.3, -0.1)
            size = random.uniform(1, 3)
            life = random.randint(100, 200)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_heart_particles(self, x, y):
        colors = ["#ff6b6b", "#ff8787", "#ffa8a8", "#ffc9c9"]
        for _ in range(15):
            angle = random.uniform(-60, 60) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(1, 3)
            speed_y = math.sin(angle) * random.uniform(1, 3) - 2
            size = random.uniform(3, 7)
            life = random.randint(40, 80)
            color = random.choice(colors)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_alert_particles(self, x, y):
        colors = ["#ff4757", "#ff6b6b", "#ffa502"]
        for _ in range(25):
            angle = random.uniform(0, 360) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(2, 5)
            speed_y = math.sin(angle) * random.uniform(2, 5)
            size = random.uniform(3, 8)
            life = random.randint(20, 40)
            color = random.choice(colors)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_success_particles(self, x, y):
        colors = ["#2ed573", "#7bed9f", "#26de81"]
        for _ in range(30):
            angle = random.uniform(0, 360) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(1, 4)
            speed_y = math.sin(angle) * random.uniform(1, 4) - 2
            size = random.uniform(2, 6)
            life = random.randint(40, 70)
            color = random.choice(colors)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_gold_particles(self, x, y):
        colors = ["#ffd700", "#ffec8b", "#ffd93d", "#f0c000"]
        for _ in range(35):
            angle = random.uniform(0, 360) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(1, 3)
            speed_y = math.sin(angle) * random.uniform(1, 3) - 1
            size = random.uniform(3, 8)
            life = random.randint(50, 80)
            color = random.choice(colors)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def create_clue_particles(self, x, y):
        colors = ["#00d4ff", "#00b894", "#55efc4", "#81ecec"]
        for _ in range(20):
            angle = random.uniform(0, 360) * math.pi / 180
            speed_x = math.cos(angle) * random.uniform(1, 2.5)
            speed_y = math.sin(angle) * random.uniform(1, 2.5) - 1.5
            size = random.uniform(2, 5)
            life = random.randint(50, 70)
            color = random.choice(colors)
            particle = Particle(self.canvas, x, y, color, size, speed_x, speed_y, life)
            self.particles.append(particle)

    def fade_in(self, callback=None):
        overlay = self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="black")
        self.canvas.tag_lower(overlay)
        
        def fade_step(alpha):
            if alpha > 0:
                alpha -= 5
                self.canvas.itemconfig(overlay, fill=f"#{hex(int(alpha))[2:].zfill(2)}000000")
                self.root.after(20, lambda: fade_step(alpha))
            else:
                self.canvas.delete(overlay)
                if callback:
                    callback()
        
        fade_step(255)

    def fade_out(self, callback=None):
        overlay = self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#00000000")
        self.canvas.tag_raise(overlay)
        
        def fade_step(alpha):
            if alpha < 255:
                alpha += 5
                self.canvas.itemconfig(overlay, fill=f"#{hex(int(alpha))[2:].zfill(2)}000000")
                self.root.after(20, lambda: fade_step(alpha))
            else:
                if callback:
                    callback()
        
        fade_step(0)

    def flash_effect(self, color="#ffffff", duration=100):
        flash = self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill=color, stipple="gray50")
        self.root.after(duration, lambda: self.canvas.delete(flash))

    def pulse_effect(self, x, y, color="#ff8906", duration=500):
        max_radius = 150
        
        def pulse_step(radius, alpha):
            if radius <= max_radius:
                circle = self.canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    fill="", outline=color, width=2
                )
                self.canvas.itemconfig(circle, outline=f"#{hex(int(alpha))[2:].zfill(2)}{color[1:]}")
                self.root.after(20, lambda: pulse_step(radius + 5, alpha - 5))
                self.root.after(40, lambda: self.canvas.delete(circle))
        
        pulse_step(10, 200)

    def draw_light_ray(self, x, y, intensity=0.3):
        rays = []
        gray = int(intensity * 255)
        color = f"#{gray:02x}{gray:02x}{gray:02x}"
        for i in range(8):
            angle = i * 45 * math.pi / 180
            length = random.randint(100, 200)
            end_x = x + math.cos(angle) * length
            end_y = y + math.sin(angle) * length
            ray = self.canvas.create_line(x, y, end_x, end_y, 
                                         fill=color,
                                         width=random.randint(2, 4))
            rays.append(ray)
        return rays

    def draw_spotlight(self, x, y, radius=300, intensity=0.2):
        gradient = []
        for i in range(9, -1, -1):
            r = radius * (i + 1) / 10
            gray = int(intensity * 255 * (1 - i / 10))
            color = f"#{gray:02x}{gray:02x}{gray:02x}"
            circle = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color,
                outline=""
            )
            gradient.append(circle)
        return gradient

    def update(self):
        if not self.running:
            return
        
        alive_particles = []
        for particle in self.particles:
            if particle.update():
                particle.remove()
                particle.draw()
                alive_particles.append(particle)
            else:
                particle.remove()
        
        self.particles = alive_particles
        
        self.root.after(33, self.update)

    def clear_all(self):
        for particle in self.particles:
            particle.remove()
        self.particles = []
        self.effects = []

    def start(self):
        self.running = True
        self.update()

    def stop(self):
        self.running = False