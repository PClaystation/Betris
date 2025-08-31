import pygame
import random

class Particle:
    def __init__(self, x, y, color, lifetime, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.alpha = 255
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.gravity = 0.1
        self.size = random.randint(2, 6)

    def update(self):
        self.age += 1
        self.velocity_y += self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.alpha = max(0, 255 - (255 * self.age // self.lifetime))

    def is_alive(self):
        return self.age < self.lifetime



    

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y , color):
        lifetime = random.randint(30,60)
        velocity_x = random.uniform(-1, 1)
        velocity_y = random.uniform(-1, -3)
        particle = Particle(x, y , color, lifetime, velocity_x, velocity_y)
        self.particles.append(particle)

    def update(self):
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def draw(self, surface):
        for particle in self.particles:
            color_with_alpha = (*particle.color[:3], particle.alpha)
            particle_surface = pygame.Surface((particle.size, particle.size), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, (particle.size // 2, particle.size // 2), particle.size // 2) 
            surface.blit(particle_surface, (particle.x - particle.size // 2, particle.y - particle.size // 2))