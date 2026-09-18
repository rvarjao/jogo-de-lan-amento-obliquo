"""Física do lançamento oblíquo: gravidade, resistência do ar e movimento do projétil.

Este módulo não depende do Pygame para desenho — lida apenas com números.
"""
import math


class Projetil:
    """Representa a bola em voo, com posição e velocidade próprias."""

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.em_movimento = False

    def lancar(self, x, y, angulo_graus, velocidade):
        """Inicia o lançamento a partir de (x, y), com o ângulo (graus) e velocidade dados."""
        angulo_rad = math.radians(angulo_graus)
        self.x = x
        self.y = y
        self.vel_x = velocidade * math.cos(angulo_rad)
        self.vel_y = -velocidade * math.sin(angulo_rad)
        self.em_movimento = True

    def parar(self, x, y):
        """Interrompe o voo e reposiciona o projétil (ex.: de volta à boca do canhão)."""
        self.em_movimento = False
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0

    def atualizar(self, gravidade, resistencia_ativada, fator_arrasto):
        """Avança um passo de física: resistência do ar, gravidade e posição."""
        if not self.em_movimento:
            return

        if resistencia_ativada:
            vel_total = math.hypot(self.vel_x, self.vel_y)
            forca_arrasto = 0.5 * fator_arrasto * (vel_total ** 2)
            if vel_total != 0:
                self.vel_x -= (self.vel_x / vel_total) * forca_arrasto
                self.vel_y -= (self.vel_y / vel_total) * forca_arrasto

        self.x += self.vel_x
        self.vel_y += gravidade
        self.y += self.vel_y


def tocou_chao(y, nivel_chao):
    """Verifica se a coordenada y já alcançou o nível do chão."""
    return y >= nivel_chao


def saiu_da_tela(x, largura):
    """Verifica se a coordenada x já saiu dos limites horizontais da tela."""
    return x > largura or x < 0
