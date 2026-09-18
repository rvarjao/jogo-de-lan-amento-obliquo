"""Ponto de entrada do jogo: inicializa o Pygame, monta os componentes e roda o loop principal.

Este módulo é o orquestrador — ele não conhece os detalhes de física, desenho de
sprites ou HUD, apenas coordena os módulos especializados a cada quadro:
    - fisica.py     -> movimento do projétil (gravidade, resistência do ar)
    - cenario.py    -> céu, nuvens e grama
    - canhao.py     -> imagem, rotação e boca do canhão
    - bola.py       -> sprite e rotação visual da bola
    - alvo.py       -> placa do alvo, colisão e reposicionamento
    - particulas.py -> fumaça/faíscas do disparo e poeira do impacto
    - hud.py         -> painéis, textos e indicadores na tela
"""
import sys

import pygame

import config as cfg
from alvo import Alvo
from bola import Bola
from canhao import Canhao
from cenario import Cenario
from fisica import Projetil, saiu_da_tela, tocou_chao
from hud import HUD
from particulas import SistemaParticulas


def main():
    pygame.init()
    tela = pygame.display.set_mode((cfg.LARGURA, cfg.ALTURA))
    pygame.display.set_caption(cfg.TITULO)
    relogio = pygame.time.Clock()

    cenario = Cenario(cfg.LARGURA, cfg.ALTURA_CEU, cfg.ALTURA_CHAO)
    canhao = Canhao(cfg.CANHAO_X, cfg.CANHAO_Y, angulo_inicial=cfg.ANGULO_INICIAL)
    bola = Bola(raio=10)
    alvo = Alvo(cfg.LARGURA, cfg.NIVEL_CHAO, diametro=cfg.ALVO_DIAMETRO, altura=cfg.ALVO_ALTURA)
    particulas = SistemaParticulas()
    hud = HUD()

    velocidade = cfg.VELOCIDADE_INICIAL
    resistencia_ativada = True
    pontos = 0
    trajetoria = []

    projetil = Projetil(*canhao.boca())

    rodando = True
    while rodando:
        # --- Cenário ---
        cenario.atualizar()
        cenario.desenhar(tela)

        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and not projetil.em_movimento:
                    boca_x, boca_y = canhao.boca()
                    projetil.lancar(boca_x, boca_y, canhao.angulo, velocidade)
                    trajetoria = []
                    bola.reiniciar_rotacao()
                    particulas.criar_disparo(boca_x, boca_y, canhao.angulo)

                if evento.key == pygame.K_r:
                    resistencia_ativada = not resistencia_ativada

        # --- Ajustes de mira (ângulo e velocidade) ---
        teclas = pygame.key.get_pressed()
        if not projetil.em_movimento:
            if teclas[pygame.K_UP]:
                canhao.ajustar_angulo(cfg.INCREMENTO_ANGULO, cfg.ANGULO_MIN, cfg.ANGULO_MAX)
            if teclas[pygame.K_DOWN]:
                canhao.ajustar_angulo(-cfg.INCREMENTO_ANGULO, cfg.ANGULO_MIN, cfg.ANGULO_MAX)
            if teclas[pygame.K_RIGHT] and velocidade < cfg.VELOCIDADE_MAX:
                velocidade += cfg.INCREMENTO_VELOCIDADE
            if teclas[pygame.K_LEFT] and velocidade > cfg.VELOCIDADE_MIN:
                velocidade -= cfg.INCREMENTO_VELOCIDADE
            # Mantém a bola parada na boca do canhão, acompanhando o ângulo de mira
            projetil.x, projetil.y = canhao.boca()

        # --- Física e colisões ---
        if projetil.em_movimento:
            projetil.atualizar(cfg.GRAVIDADE, resistencia_ativada, cfg.FATOR_ARRASTO)
            trajetoria.append((int(projetil.x), int(projetil.y)))
            bola.atualizar_rotacao(projetil.vel_x)

            if alvo.colide(projetil.x, projetil.y):
                pontos += 1
                alvo.reposicionar()
                projetil.parar(*canhao.boca())
                trajetoria = []
            elif tocou_chao(projetil.y, cfg.NIVEL_CHAO) or saiu_da_tela(projetil.x, cfg.LARGURA):
                if tocou_chao(projetil.y, cfg.NIVEL_CHAO):
                    particulas.criar_poeira(projetil.x, cfg.NIVEL_CHAO)
                projetil.parar(*canhao.boca())

        particulas.atualizar(cfg.GRAVIDADE)

        # --- Renderização ---
        alvo.desenhar(tela)

        for ponto in trajetoria:
            pygame.draw.circle(tela, cfg.PRETO, ponto, 2)

        canhao.desenhar(tela)

        if projetil.em_movimento:
            bola.desenhar(tela, projetil.x, projetil.y)

        particulas.desenhar(tela)

        hud.desenhar(tela, cfg.LARGURA, cfg.ALTURA, canhao.angulo, velocidade, resistencia_ativada, pontos)

        pygame.display.flip()
        relogio.tick(cfg.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
