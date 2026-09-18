"""O canhão: imagem, rotação em torno da base e cálculo da posição da boca do cano."""
import math
from pathlib import Path

import pygame

DIRETORIO_ASSETS = Path(__file__).parent

# Ponto da base (bola de trás do canhão) e da boca do cano na imagem original (canhao.png),
# medidos em pixels da imagem original antes de qualquer escala.
PIVO_ORIGINAL = (334, 910)
BOCA_ORIGINAL = (1438, 910)


class Canhao:
    """Representa o canhão: posição, ângulo de mira e a imagem já pronta para rotacionar."""

    def __init__(self, x, y, angulo_inicial=45, escala=0.09, arquivo_imagem="canhao.png"):
        self.x = x
        self.y = y
        self.angulo = angulo_inicial

        imagem_original = pygame.image.load(str(DIRETORIO_ASSETS / arquivo_imagem)).convert_alpha()
        self.imagem = pygame.transform.smoothscale(
            imagem_original,
            (
                int(imagem_original.get_width() * escala),
                int(imagem_original.get_height() * escala),
            ),
        )
        # Ponto da base na imagem já escalada, usado como pivô de rotação
        self.pivo = (PIVO_ORIGINAL[0] * escala, PIVO_ORIGINAL[1] * escala)
        # Distância entre a base e a boca do cano, já escalada
        self.comprimento_cano = (BOCA_ORIGINAL[0] - PIVO_ORIGINAL[0]) * escala

    def ajustar_angulo(self, delta, minimo=0, maximo=90):
        self.angulo = max(minimo, min(maximo, self.angulo + delta))

    def boca(self):
        """Retorna a posição (x, y) da ponta do cano, de onde a bola deve ser lançada."""
        angulo_rad = math.radians(self.angulo)
        boca_x = self.x + self.comprimento_cano * math.cos(angulo_rad)
        boca_y = self.y - self.comprimento_cano * math.sin(angulo_rad)
        return boca_x, boca_y

    def desenhar(self, superficie):
        """Desenha a imagem do canhão rotacionada em torno do pivô (base do canhão),
        mantendo a base fixa em (self.x, self.y)."""
        pos = (self.x, self.y)
        rect_imagem = self.imagem.get_rect(topleft=(pos[0] - self.pivo[0], pos[1] - self.pivo[1]))
        offset_centro_pivo = pygame.math.Vector2(pos) - rect_imagem.center
        offset_rotacionado = offset_centro_pivo.rotate(-self.angulo)
        centro_rotacionado = (pos[0] - offset_rotacionado.x, pos[1] - offset_rotacionado.y)
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        rect_rotacionado = imagem_rotacionada.get_rect(center=centro_rotacionado)
        superficie.blit(imagem_rotacionada, rect_rotacionado)
