"""Configurações e constantes globais do jogo."""

# --- Janela ---
LARGURA = 1000
ALTURA = 600
TITULO = "Jogo de Arremesso Oblíquo com Alvo"
FPS = 60

# --- Cenário ---
ALTURA_CHAO = 50
ALTURA_CEU = ALTURA - ALTURA_CHAO
NIVEL_CHAO = ALTURA - ALTURA_CHAO  # coordenada y onde a grama começa

# --- Física ---
GRAVIDADE = 0.5
FATOR_ARRASTO = 0.005  # controla a força da resistência do ar (menor = menos resistência)

# --- Canhão ---
CANHAO_X = 50
CANHAO_Y = NIVEL_CHAO
ANGULO_INICIAL = 45
VELOCIDADE_INICIAL = 15
ANGULO_MIN, ANGULO_MAX = 0, 90
VELOCIDADE_MIN, VELOCIDADE_MAX = 5, 30
INCREMENTO_ANGULO = 1
INCREMENTO_VELOCIDADE = 0.2

# --- Alvo ---
ALVO_DIAMETRO = 40
ALVO_ALTURA = 15

# --- Cores (RGB) ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
AMARELO = (255, 215, 0)
