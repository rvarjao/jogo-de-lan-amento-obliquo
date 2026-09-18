"""O alvo: placa 'bullseye' com anéis concêntricos, poste, sombra e brilho pulsante."""
import math
import random

import pygame


def gerar_sprite_alvo(raio):
    """Gera um disco de alvo em anéis concêntricos (vermelho/branco/vermelho/dourado),
    com um leve sombreamento radial para dar volume, como uma placa de tiro ao alvo."""
    tam = raio * 2
    sprite = pygame.Surface((tam, tam), pygame.SRCALPHA)
    centro = pygame.math.Vector2(raio, raio)

    aneis = [
        (1.00, (200, 30, 30)),
        (0.75, (245, 245, 240)),
        (0.50, (200, 30, 30)),
        (0.25, (255, 205, 60)),
    ]

    for y in range(tam):
        for x in range(tam):
            pos = pygame.math.Vector2(x + 0.5, y + 0.5)
            dist_centro = pos.distance_to(centro)
            if dist_centro > raio:
                continue

            fracao = dist_centro / raio
            cor_base = aneis[0][1]
            for limite, cor_anel in aneis:
                if fracao <= limite:
                    cor_base = cor_anel

            # Leve sombreamento para dar volume à placa
            sombreado = 0.75 + 0.25 * (1 - fracao)
            cor = (
                min(255, int(cor_base[0] * sombreado)),
                min(255, int(cor_base[1] * sombreado)),
                min(255, int(cor_base[2] * sombreado)),
            )
            sprite.set_at((x, y), (*cor, 255))

    # Contorno escuro para destacar a silhueta do alvo
    pygame.draw.circle(sprite, (40, 20, 20), (raio, raio), raio, width=2)

    return sprite


class Alvo:
    """Posição, colisão e desenho do alvo de tiro ao alvo."""

    def __init__(self, largura_tela, y, diametro=40, altura=15):
        self.diametro = diametro
        self.raio = diametro // 2
        self.altura = altura
        self.y = y
        self.largura_tela = largura_tela
        self.sprite = gerar_sprite_alvo(self.raio)
        self.x = 0
        self.reposicionar()

    def reposicionar(self):
        """Sorteia uma nova posição horizontal aleatória para o alvo."""
        self.x = random.randint(300, self.largura_tela - self.diametro)

    def colide(self, bola_x, bola_y):
        """Verifica se a bola, na posição dada, atingiu a área do alvo."""
        return (
            self.x <= bola_x <= self.x + self.diametro
            and self.y - 10 <= bola_y <= self.y + self.altura
        )

    def desenhar(self, superficie):
        """Desenha o alvo como uma placa circular sobre um poste, cravada na grama,
        com sombra no chão e um brilho pulsante para chamar atenção do jogador."""
        centro_x = self.x + self.diametro // 2
        centro_y = self.y + 2

        # Sombra no chão, projetada pela base do poste
        sombra = pygame.Surface((self.diametro, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sombra, (0, 0, 0, 90), sombra.get_rect())
        superficie.blit(sombra, (self.x, self.y + self.altura - 4))

        # Poste de madeira que sustenta a placa
        poste_largura = 4
        pygame.draw.rect(
            superficie, (110, 75, 45),
            (centro_x - poste_largura // 2, centro_y, poste_largura, self.altura),
        )

        # Brilho pulsante ao redor do alvo (efeito puramente visual)
        pulso = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2  # oscila entre 0 e 1
        raio_brilho = self.raio + 4 + int(3 * pulso)
        brilho = pygame.Surface((raio_brilho * 2, raio_brilho * 2), pygame.SRCALPHA)
        alpha_brilho = int(60 + 60 * pulso)
        pygame.draw.circle(brilho, (255, 240, 150, alpha_brilho), (raio_brilho, raio_brilho), raio_brilho)
        superficie.blit(brilho, (centro_x - raio_brilho, centro_y - raio_brilho))

        # Placa do alvo (anéis concêntricos)
        rect_alvo = self.sprite.get_rect(center=(centro_x, centro_y))
        superficie.blit(self.sprite, rect_alvo)
