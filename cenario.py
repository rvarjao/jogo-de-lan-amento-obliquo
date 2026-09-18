"""Cenário do jogo: céu com gradiente, nuvens à deriva e grama texturizada."""
import random

import pygame

COR_CEU_TOPO = (90, 150, 230)
COR_CEU_HORIZONTE = (200, 225, 245)
COR_GRAMA_CLARA = (86, 170, 60)
COR_GRAMA_ESCURA = (48, 120, 40)
COR_TERRA = (94, 68, 46)


def _gerar_ceu(largura, altura_ceu):
    """Gera um céu com gradiente vertical, do azul mais forte no topo até
    um tom quase branco perto do horizonte."""
    superficie = pygame.Surface((largura, altura_ceu))
    for y in range(altura_ceu):
        fator = y / altura_ceu
        cor = (
            int(COR_CEU_TOPO[0] + (COR_CEU_HORIZONTE[0] - COR_CEU_TOPO[0]) * fator),
            int(COR_CEU_TOPO[1] + (COR_CEU_HORIZONTE[1] - COR_CEU_TOPO[1]) * fator),
            int(COR_CEU_TOPO[2] + (COR_CEU_HORIZONTE[2] - COR_CEU_TOPO[2]) * fator),
        )
        pygame.draw.line(superficie, cor, (0, y), (largura, y))
    return superficie


def _gerar_grama(largura, altura_chao):
    """Gera uma faixa de grama com gradiente e fios aleatórios para dar textura,
    além de uma fina camada de terra na base."""
    superficie = pygame.Surface((largura, altura_chao))
    for y in range(altura_chao):
        fator = y / altura_chao
        cor = (
            int(COR_GRAMA_CLARA[0] + (COR_GRAMA_ESCURA[0] - COR_GRAMA_CLARA[0]) * fator),
            int(COR_GRAMA_CLARA[1] + (COR_GRAMA_ESCURA[1] - COR_GRAMA_CLARA[1]) * fator),
            int(COR_GRAMA_CLARA[2] + (COR_GRAMA_ESCURA[2] - COR_GRAMA_CLARA[2]) * fator),
        )
        pygame.draw.line(superficie, cor, (0, y), (largura, y))

    # Fios de grama aleatórios (pequenos traços verticais mais escuros/claros)
    rng = random.Random(42)  # semente fixa para textura consistente a cada execução
    for _ in range(largura // 2):
        x = rng.randint(0, largura - 1)
        y = rng.randint(0, altura_chao - 6)
        altura_fio = rng.randint(3, 7)
        tom = rng.choice([COR_GRAMA_ESCURA, (70, 150, 50), (110, 190, 80)])
        pygame.draw.line(superficie, tom, (x, y), (x, y + altura_fio), 1)

    # Faixa de terra na base, simulando a base do gramado
    pygame.draw.rect(superficie, COR_TERRA, (0, altura_chao - 4, largura, 4))

    return superficie


def _gerar_nuvem(largura_base):
    """Gera uma nuvem fofa a partir de vários círculos brancos semitransparentes
    sobrepostos, formando um formato orgânico e irregular."""
    altura_base = int(largura_base * 0.55)
    superficie = pygame.Surface((largura_base, altura_base), pygame.SRCALPHA)
    rng = random.Random()
    num_lobulos = rng.randint(5, 7)
    for i in range(num_lobulos):
        cx = largura_base * (0.15 + 0.7 * i / max(1, num_lobulos - 1))
        cy = altura_base * rng.uniform(0.45, 0.65)
        raio = largura_base * rng.uniform(0.18, 0.28)
        pygame.draw.circle(superficie, (255, 255, 255, 210), (int(cx), int(cy)), int(raio))
    # Sombra sutil na parte inferior da nuvem, para dar volume
    sombra = pygame.Surface((largura_base, altura_base), pygame.SRCALPHA)
    for i in range(num_lobulos):
        cx = largura_base * (0.15 + 0.7 * i / max(1, num_lobulos - 1))
        cy = altura_base * rng.uniform(0.55, 0.7)
        raio = largura_base * rng.uniform(0.14, 0.2)
        pygame.draw.circle(sombra, (170, 185, 200, 90), (int(cx), int(cy)), int(raio))
    superficie.blit(sombra, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)
    return superficie


class Cenario:
    """Mantém e desenha o céu, as nuvens (com deriva lenta) e a grama."""

    def __init__(self, largura, altura_ceu, altura_chao, num_nuvens=4):
        self.largura = largura
        self.altura_ceu = altura_ceu
        self.ceu_sprite = _gerar_ceu(largura, altura_ceu)
        self.grama_sprite = _gerar_grama(largura, altura_chao)

        self.nuvens = []
        for _ in range(num_nuvens):
            largura_nuvem = random.randint(90, 160)
            self.nuvens.append({
                "sprite": _gerar_nuvem(largura_nuvem),
                "x": random.uniform(0, largura),
                "y": random.uniform(20, altura_ceu * 0.55),
                "velocidade": random.uniform(0.15, 0.4),
            })

    def atualizar(self):
        for nuvem in self.nuvens:
            nuvem["x"] += nuvem["velocidade"]
            if nuvem["x"] > self.largura + nuvem["sprite"].get_width():
                nuvem["x"] = -nuvem["sprite"].get_width()

    def desenhar(self, superficie):
        superficie.blit(self.ceu_sprite, (0, 0))
        for nuvem in self.nuvens:
            superficie.blit(nuvem["sprite"], (nuvem["x"], nuvem["y"]))
        superficie.blit(self.grama_sprite, (0, self.altura_ceu))
