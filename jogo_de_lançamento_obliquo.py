import pygame
import math
import random
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Janela
LARGURA, ALTURA = 1000, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Arremesso Oblíquo com Alvo")
relogio = pygame.time.Clock()

# Cores (RGB)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
AMARELO = (255, 215, 0)

# Constantes da Física do Jogo
GRAVIDADE = 0.5  

# --- NOVAS VARIÁVEIS PARA A RESISTÊNCIA DO AR ---
resistencia_ativada = True
FATOR_ARRASTO = 0.005  # Controla a força do ar (valores menores = menos resistência)

# Variáveis do Canhão
canhon_x = 50
canhon_y = ALTURA - 50

# --- IMAGEM DO CANHÃO ---
# A imagem já vem com o cano paralelo ao chão (apontando para a direita, ângulo 0°)
canhao_img_original = pygame.image.load("canhao.png").convert_alpha()
ESCALA_CANHAO = 0.09
canhao_img = pygame.transform.smoothscale(
    canhao_img_original,
    (
        int(canhao_img_original.get_width() * ESCALA_CANHAO),
        int(canhao_img_original.get_height() * ESCALA_CANHAO),
    ),
)
# Ponto da base (bola de trás do canhão) na imagem original, usado como pivô de rotação
PIVO_CANHAO = (334 * ESCALA_CANHAO, 910 * ESCALA_CANHAO)
# Distância entre a base e a boca (ponta do cano) na imagem original, já escalada
COMPRIMENTO_CANO = (1438 - 334) * ESCALA_CANHAO


def desenha_canhao_rotacionado(superficie, imagem, pos, pivo, angulo):
    """Desenha a imagem do canhão rotacionada em torno do pivô (base do canhão)."""
    rect_imagem = imagem.get_rect(topleft=(pos[0] - pivo[0], pos[1] - pivo[1]))
    offset_centro_pivo = pygame.math.Vector2(pos) - rect_imagem.center
    offset_rotacionado = offset_centro_pivo.rotate(-angulo)
    centro_rotacionado = (pos[0] - offset_rotacionado.x, pos[1] - offset_rotacionado.y)
    imagem_rotacionada = pygame.transform.rotate(imagem, angulo)
    rect_rotacionado = imagem_rotacionada.get_rect(center=centro_rotacionado)
    superficie.blit(imagem_rotacionada, rect_rotacionado)


def posicao_boca_canhao(angulo):
    """Calcula a posição da boca do canhão (ponta do cano) para o ângulo atual."""
    angulo_rad = math.radians(angulo)
    boca_x = canhon_x + COMPRIMENTO_CANO * math.cos(angulo_rad)
    boca_y = canhon_y - COMPRIMENTO_CANO * math.sin(angulo_rad)
    return boca_x, boca_y


# --- SPRITE DA BOLA DE CANHÃO (esfera preta com sombreamento e brilho) ---
def gerar_sprite_bola(raio):
    """Gera uma esfera preta com sombreamento radial e um brilho especular,
    simulando o reflexo de luz em uma bola de canhão de ferro fundido."""
    tam = raio * 2
    sprite = pygame.Surface((tam, tam), pygame.SRCALPHA)
    centro = pygame.math.Vector2(raio, raio)
    luz = pygame.math.Vector2(raio * 0.65, raio * 0.65)  # brilho no canto superior-esquerdo

    # Pequenas marcas mais escuras (fixas na superfície) para tornar a rotação visível
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


BOLA_RAIO = 10
BOLA_SPRITE = gerar_sprite_bola(BOLA_RAIO)

# Rotação puramente visual da bola durante o voo (não interfere na física)
rotacao_bola = 0.0
GRAUS_ROTACAO_POR_VELOCIDADE = 4.0


def desenha_bola(superficie, x, y, angulo_rotacao=0.0):
    sprite_rotacionado = pygame.transform.rotate(BOLA_SPRITE, angulo_rotacao)
    rect = sprite_rotacionado.get_rect(center=(int(x), int(y)))
    superficie.blit(sprite_rotacionado, rect)


# --- GERADOR DE PARTÍCULAS DO DISPARO (fumaça e faíscas) ---
CORES_FAGULHA = [(255, 220, 80), (255, 160, 40), (255, 90, 20)]
CORES_FUMACA = [(120, 120, 120), (160, 160, 160), (200, 200, 200)]
particulas = []


def criar_particulas_disparo(x, y, angulo):
    """Cria uma explosão de partículas (faíscas + fumaça) na boca do canhão."""
    angulo_rad = math.radians(angulo)
    dir_x, dir_y = math.cos(angulo_rad), -math.sin(angulo_rad)

    # Faíscas: rápidas, pequenas, na direção do disparo com pouco espalhamento
    for _ in range(15):
        espalhamento = math.radians(random.uniform(-12, 12))
        vx = dir_x * math.cos(espalhamento) - dir_y * math.sin(espalhamento)
        vy = dir_x * math.sin(espalhamento) + dir_y * math.cos(espalhamento)
        velocidade_particula = random.uniform(4, 9)
        particulas.append({
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
        particulas.append({
            "x": x, "y": y,
            "vx": vx * velocidade_particula,
            "vy": vy * velocidade_particula,
            "vida": random.randint(25, 45),
            "vida_total": 45,
            "raio": random.uniform(4, 8),
            "cor": random.choice(CORES_FUMACA),
            "arrasto": 0.96,
        })


def atualizar_particulas():
    for p in particulas:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vx"] *= p["arrasto"]
        p["vy"] *= p["arrasto"]
        p["vy"] += GRAVIDADE * 0.1  # leve influência da gravidade
        p["vida"] -= 1
    particulas[:] = [p for p in particulas if p["vida"] > 0]


def desenha_particulas(superficie):
    for p in particulas:
        alpha = max(0, int(255 * (p["vida"] / p["vida_total"])))
        raio = max(1, int(p["raio"]))
        tam = raio * 2
        superficie_particula = pygame.Surface((tam, tam), pygame.SRCALPHA)
        pygame.draw.circle(superficie_particula, (*p["cor"], alpha), (raio, raio), raio)
        superficie.blit(superficie_particula, (int(p["x"]) - raio, int(p["y"]) - raio))

# Parâmetros de Lançamento Iniciais
angulo = 45        
velocidade = 15     

# Estado da Bola
bola_x, bola_y = posicao_boca_canhao(angulo)
vel_x = 0
vel_y = 0
em_movimento = False
trajetoria = []  

# --- VARIÁVEIS: ALVO E PONTUAÇÃO ---
alvo_largura = 40
alvo_altura = 15
# Reposiciona o alvo aleatoriamente na metade direita da tela, em cima do chão
alvo_x = random.randint(400, LARGURA - alvo_largura)
alvo_y = ALTURA - 50  # Alinhado com o topo do chão
pontos = 0

fonte = pygame.font.SysFont("Arial", 20)
fonte_placar = pygame.font.SysFont("Arial", 24, bold=True)

# Loop Principal do Jogo
rodando = True
while rodando:
    tela.fill(BRANCO)
    
    # Desenha o Chão
    pygame.draw.rect(tela, VERDE, (0, ALTURA - 50, LARGURA, 50))
    
    # Captura de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            pygame.quit()
            sys.exit()
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not em_movimento:
                angulo_rad = math.radians(angulo)
                bola_x, bola_y = posicao_boca_canhao(angulo)
                vel_x = velocidade * math.cos(angulo_rad)
                vel_y = -velocidade * math.sin(angulo_rad)
                em_movimento = True
                trajetoria = []
                rotacao_bola = 0.0
                criar_particulas_disparo(bola_x, bola_y, angulo)
            
            # --- INTERRUPTOR DA RESISTÊNCIA DO AR ---
            if evento.key == pygame.K_r:
                resistencia_ativada = not resistencia_ativada

    # Ajustes de ângulo e força
    teclas = pygame.key.get_pressed()
    if not em_movimento:
        if teclas[pygame.K_UP] and angulo < 90:
            angulo += 1
        if teclas[pygame.K_DOWN] and angulo > 0:
            angulo -= 1
        if teclas[pygame.K_RIGHT] and velocidade < 30:
            velocidade += 0.2
        if teclas[pygame.K_LEFT] and velocidade > 5:
            velocidade -= 0.2
        # Mantém a bola parada na boca do canhão, acompanhando o ângulo de mira
        bola_x, bola_y = posicao_boca_canhao(angulo)

    # Atualização da Física e Detecção de Colisão
    if em_movimento:
        # --- CÁLCULO DA RESISTÊNCIA DO AR ---
        if resistencia_ativada:
            # Velocidade total atual da bola (vetor)
            vel_total = math.sqrt(vel_x**2 + vel_y**2)
            
            # Força de arrasto proporcional ao quadrado da velocidade
            forca_arrasto = 0.5 * FATOR_ARRASTO * (vel_total**2)
            
            # Evita divisão por zero caso a bola pare no ar
            if vel_total != 0:
                # Aplica a perda de velocidade de forma contrária ao movimento atual
                vel_x -= (vel_x / vel_total) * forca_arrasto
                vel_y -= (vel_y / vel_total) * forca_arrasto

        # Física padrão (Gravidade e Posição)
        bola_x += vel_x
        vel_y += GRAVIDADE
        bola_y += vel_y
        trajetoria.append((int(bola_x), int(bola_y)))

        # Rotação da bola: efeito puramente visual, não interfere na física do lançamento
        rotacao_bola -= vel_x * GRAUS_ROTACAO_POR_VELOCIDADE
        
        # 1. DETECÇÃO DE ACERTO NO ALVO (Colisão da Bola com o Retângulo do Alvo)
        if (alvo_x <= bola_x <= alvo_x + alvo_largura) and (alvo_y - 10 <= bola_y <= alvo_y + alvo_altura):
            pontos += 1
            # Sorteia uma nova posição para o alvo
            alvo_x = random.randint(300, LARGURA - alvo_largura)
            # Reseta a bola
            em_movimento = False
            bola_x, bola_y = posicao_boca_canhao(angulo)
            trajetoria = []

        # 2. Condição de parada padrão (se errar o alvo e tocar no chão/sair da tela)
        elif bola_y >= ALTURA - 50 or bola_x > LARGURA or bola_x < 0:
            em_movimento = False
            bola_x, bola_y = posicao_boca_canhao(angulo)

    # Atualiza as partículas do disparo (fumaça e faíscas)
    atualizar_particulas()

    # --- RENDERIZAÇÃO ---
    
    # Desenha o Alvo
    pygame.draw.rect(tela, VERMELHO, (alvo_x, alvo_y, alvo_largura, alvo_altura))
    pygame.draw.rect(tela, AMARELO, (alvo_x + 10, alvo_y, alvo_largura - 20, alvo_altura))
    
    # Desenha a Trajetória anterior
    for ponto in trajetoria:
        pygame.draw.circle(tela, PRETO, ponto, 2)
        
    # Desenha o Canhão (imagem rotacionada de acordo com o ângulo de mira)
    desenha_canhao_rotacionado(tela, canhao_img, (canhon_x, canhon_y), PIVO_CANHAO, angulo)
    
    # Desenha a Bola (somente enquanto estiver em voo, após o disparo)
    if em_movimento:
        desenha_bola(tela, bola_x, bola_y, rotacao_bola)

    # Desenha as Partículas do disparo (por cima de tudo)
    desenha_particulas(tela)
        
    # Textos da Interface
    txt_angulo = fonte.render(f"Ângulo: {angulo}° (Setas Cima/Baixo)", True, PRETO)
    txt_velocidade = fonte.render(f"Velocidade: {velocidade:.1f} (Setas Esq/Dir)", True, PRETO)
    txt_instrucoes = fonte.render("ESPAÇO: Atirar", True, PRETO)
    
    # --- TEXTO DO STATUS DA RESISTÊNCIA ---
    status_ar = "ATIVADA" if resistencia_ativada else "DESATIVADA"
    cor_status = VERDE if resistencia_ativada else VERMELHO
    txt_resistencia = fonte.render(f"Resistência do Ar [Tecla R]: {status_ar}", True, cor_status)
    
    # Exibe o Placar de Pontos
    txt_placar = fonte_placar.render(f"PONTOS: {pontos}", True, AZUL)
    
    tela.blit(txt_angulo, (20, 20))
    tela.blit(txt_velocidade, (20, 50))
    tela.blit(txt_instrucoes, (20, 80))
    tela.blit(txt_resistencia, (20, 110)) # Nova linha de texto
    tela.blit(txt_placar, (LARGURA - 160, 20)) 
    
    pygame.display.flip()
    relogio.tick(60)
