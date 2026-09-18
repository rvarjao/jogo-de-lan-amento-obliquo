"""Sistemas de partículas: fumaça/faíscas do disparo e poeira do impacto no chão."""
import math
import random

import pygame

CORES_FAGULHA = [(255, 220, 80), (255, 160, 40), (255, 90, 20)]
CORES_FUMACA = [(120, 120, 120), (160, 160, 160), (200, 200, 200)]
CORES_POEIRA = [(194, 178, 128), (210, 180, 140), (166, 145, 100)]


class SistemaParticulas:
    """Mantém, atualiza e desenha todas as partículas visuais do jogo."""

    def __init__(self):
        self.particulas = []

    def criar_disparo(self, x, y, angulo):
        """Cria uma explosão de partículas (faíscas + fumaça) na boca do canhão."""
        angulo_rad = math.radians(angulo)
        dir_x, dir_y = math.cos(angulo_rad), -math.sin(angulo_rad)

        # Faíscas: rápidas, pequenas, na direção do disparo com pouco espalhamento
        for _ in range(15):
            espalhamento = math.radians(random.uniform(-12, 12))
            vx = dir_x * math.cos(espalhamento) - dir_y * math.sin(espalhamento)
            vy = dir_x * math.sin(espalhamento) + dir_y * math.cos(espalhamento)
            velocidade_particula = random.uniform(4, 9)
            self.particulas.append({
                "x": x, "y": y,
                "vx": vx * velocidade_particula,
                "vy": vy * velocidade_particula,
                "vida": random.randint(10, 20),
                "vida_total": 20,
                "raio": random.uniform(2, 4),
                "cor": random.choice(CORES_FAGULHA),
                "arrasto": 0.90,
            })

        # Fumaça: mais lenta, maior espalhamento, dura mais tempo
        for _ in range(12):
            espalhamento = math.radians(random.uniform(-35, 35))
            vx = dir_x * math.cos(espalhamento) - dir_y * math.sin(espalhamento)
            vy = dir_x * math.sin(espalhamento) + dir_y * math.cos(espalhamento)
            velocidade_particula = random.uniform(1, 3)
            self.particulas.append({
                "x": x, "y": y,
                "vx": vx * velocidade_particula,
                "vy": vy * velocidade_particula,
                "vida": random.randint(25, 45),
                "vida_total": 45,
                "raio": random.uniform(4, 8),
                "cor": random.choice(CORES_FUMACA),
                "arrasto": 0.96,
            })

    def criar_poeira(self, x, y):
        """Levanta uma nuvem de poeira no ponto onde a bola toca o chão."""
        for _ in range(18):
            angulo_rad = math.radians(random.uniform(200, 340))  # leque para cima, entre os dois lados
            velocidade_particula = random.uniform(1, 4)
            vx = math.cos(angulo_rad) * velocidade_particula
            vy = math.sin(angulo_rad) * velocidade_particula
            self.particulas.append({
                "x": x, "y": y,
                "vx": vx,
                "vy": vy,
                "vida": random.randint(20, 40),
                "vida_total": 40,
                "raio": random.uniform(3, 7),
                "cor": random.choice(CORES_POEIRA),
                "arrasto": 0.92,
            })

    def atualizar(self, gravidade):
        for p in self.particulas:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vx"] *= p["arrasto"]
            p["vy"] *= p["arrasto"]
            p["vy"] += gravidade * 0.1  # leve influência da gravidade
            p["vida"] -= 1
        self.particulas[:] = [p for p in self.particulas if p["vida"] > 0]

    def desenhar(self, superficie):
        for p in self.particulas:
            alpha = max(0, int(255 * (p["vida"] / p["vida_total"])))
            raio = max(1, int(p["raio"]))
            tam = raio * 2
            superficie_particula = pygame.Surface((tam, tam), pygame.SRCALPHA)
            pygame.draw.circle(superficie_particula, (*p["cor"], alpha), (raio, raio), raio)
            superficie.blit(superficie_particula, (int(p["x"]) - raio, int(p["y"]) - raio))
