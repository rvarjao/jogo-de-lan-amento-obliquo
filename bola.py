"""Sprite e desenho da bola de canhão: esfera preta com brilho, sombreamento e rotação visual."""
import pygame


def gerar_sprite_bola(raio):
    """Gera uma esfera preta com sombreamento radial, brilho especular e pequenas
    marcas na casca, usadas para que a rotação visual da bola seja perceptível."""
    tam = raio * 2
    sprite = pygame.Surface((tam, tam), pygame.SRCALPHA)
    centro = pygame.math.Vector2(raio, raio)
    luz = pygame.math.Vector2(raio * 0.65, raio * 0.65)  # brilho no canto superior-esquerdo

    manchas = [
        (pygame.math.Vector2(raio * 1.35, raio * 0.55), raio * 0.16),
        (pygame.math.Vector2(raio * 0.45, raio * 1.5), raio * 0.13),
        (pygame.math.Vector2(raio * 1.55, raio * 1.55), raio * 0.11),
    ]

    for y in range(tam):
        for x in range(tam):
            pos = pygame.math.Vector2(x + 0.5, y + 0.5)
            dist_centro = pos.distance_to(centro)
            if dist_centro > raio:
                continue

            # Sombreamento: mais escuro nas bordas, dando volume esférico
            sombreado = 1 - (dist_centro / raio) * 0.8
            base = 12 + int(28 * sombreado)

            # Brilho especular concentrado, simulando reflexo de luz
            dist_luz = pos.distance_to(luz)
            brilho = max(0.0, 1 - dist_luz / (raio * 0.55))
            brilho = brilho ** 4
            cor = min(255, base + int(230 * brilho))

            # Marcas escuras fixas na "casca" da bola, usadas para perceber a rotação
            for centro_mancha, raio_mancha in manchas:
                if pos.distance_to(centro_mancha) < raio_mancha:
                    cor = max(0, cor - 40)
                    break

            sprite.set_at((x, y), (cor, cor, cor, 255))

    return sprite


class Bola:
    """Estado visual da bola de canhão: sprite pré-renderizado e rotação de voo."""

    GRAUS_ROTACAO_POR_VELOCIDADE = 4.0

    def __init__(self, raio=10):
        self.raio = raio
        self.sprite = gerar_sprite_bola(raio)
        self.rotacao = 0.0

    def reiniciar_rotacao(self):
        self.rotacao = 0.0

    def atualizar_rotacao(self, vel_x):
        """Gira a bola de acordo com a velocidade horizontal do projétil.
        Efeito puramente visual: não entra em nenhum cálculo de física."""
        self.rotacao -= vel_x * self.GRAUS_ROTACAO_POR_VELOCIDADE

    def desenhar(self, superficie, x, y):
        sprite_rotacionado = pygame.transform.rotate(self.sprite, self.rotacao)
        rect = sprite_rotacionado.get_rect(center=(int(x), int(y)))
        superficie.blit(sprite_rotacionado, rect)
