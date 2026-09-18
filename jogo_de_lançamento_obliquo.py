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

# --- CENÁRIO: CÉU COM GRADIENTE ---
ALTURA_CHAO = 50
ALTURA_CEU = ALTURA - ALTURA_CHAO
COR_CEU_TOPO = (90, 150, 230)
COR_CEU_HORIZONTE = (200, 225, 245)


def gerar_ceu(largura, altura_ceu):
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


CEU_SPRITE = gerar_ceu(LARGURA, ALTURA_CEU)


# --- CENÁRIO: GRAMA COM TEXTURA ---
COR_GRAMA_CLARA = (86, 170, 60)
COR_GRAMA_ESCURA = (48, 120, 40)
COR_TERRA = (94, 68, 46)


def gerar_grama(largura, altura_chao):
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


GRAMA_SPRITE = gerar_grama(LARGURA, ALTURA_CHAO)


# --- CENÁRIO: NUVENS ---
def gerar_nuvem(largura_base):
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


# Cada nuvem: sprite, posição x/y, velocidade horizontal de deriva
NUVENS = []
for _ in range(4):
    largura_nuvem = random.randint(90, 160)
    sprite_nuvem = gerar_nuvem(largura_nuvem)
    NUVENS.append({
        "sprite": sprite_nuvem,
        "x": random.uniform(0, LARGURA),
        "y": random.uniform(20, ALTURA_CEU * 0.55),
        "velocidade": random.uniform(0.15, 0.4),
    })


def atualiza_nuvens():
    for nuvem in NUVENS:
        nuvem["x"] += nuvem["velocidade"]
        if nuvem["x"] > LARGURA + nuvem["sprite"].get_width():
            nuvem["x"] = -nuvem["sprite"].get_width()


def desenha_cenario(superficie):
    superficie.blit(CEU_SPRITE, (0, 0))
    for nuvem in NUVENS:
        superficie.blit(nuvem["sprite"], (nuvem["x"], nuvem["y"]))
    superficie.blit(GRAMA_SPRITE, (0, ALTURA_CEU))

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


# --- SPRITE DO ALVO (disco de tiro ao alvo, estilo "bullseye") ---
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


ALVO_DIAMETRO = 40
ALVO_RAIO = ALVO_DIAMETRO // 2
ALVO_SPRITE = gerar_sprite_alvo(ALVO_RAIO)


def desenha_alvo(superficie, alvo_x, alvo_y, alvo_largura, alvo_altura):
    """Desenha o alvo como uma placa circular sobre um poste, cravada na grama,
    com sombra no chão e um brilho pulsante para chamar atenção do jogador."""
    centro_x = alvo_x + alvo_largura // 2
    centro_y = alvo_y + 2

    # Sombra no chão, projetada pela base do poste
    sombra = pygame.Surface((alvo_largura, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 90), sombra.get_rect())
    superficie.blit(sombra, (alvo_x, alvo_y + alvo_altura - 4))

    # Poste de madeira que sustenta a placa
    poste_largura = 4
    pygame.draw.rect(
        superficie, (110, 75, 45),
        (centro_x - poste_largura // 2, centro_y, poste_largura, alvo_altura),
    )

    # Brilho pulsante ao redor do alvo (efeito puramente visual)
    pulso = (math.sin(pygame.time.get_ticks() / 200) + 1) / 2  # oscila entre 0 e 1
    raio_brilho = ALVO_RAIO + 4 + int(3 * pulso)
    brilho = pygame.Surface((raio_brilho * 2, raio_brilho * 2), pygame.SRCALPHA)
    alpha_brilho = int(60 + 60 * pulso)
    pygame.draw.circle(brilho, (255, 240, 150, alpha_brilho), (raio_brilho, raio_brilho), raio_brilho)
    superficie.blit(brilho, (centro_x - raio_brilho, centro_y - raio_brilho))

    # Placa do alvo (anéis concêntricos)
    rect_alvo = ALVO_SPRITE.get_rect(center=(centro_x, centro_y))
    superficie.blit(ALVO_SPRITE, rect_alvo)


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


# --- GERADOR DE PARTÍCULAS DE IMPACTO (poeira ao atingir o chão) ---
CORES_POEIRA = [(194, 178, 128), (210, 180, 140), (166, 145, 100)]


def criar_particulas_poeira(x, y):
    """Levanta uma nuvem de poeira no ponto onde a bola toca o chão."""
    for _ in range(18):
        angulo_rad = math.radians(random.uniform(200, 340))  # leque para cima, entre os dois lados
        velocidade_particula = random.uniform(1, 4)
        vx = math.cos(angulo_rad) * velocidade_particula
        vy = math.sin(angulo_rad) * velocidade_particula
        particulas.append({
            "x": x, "y": y,
            "vx": vx,
            "vy": vy,
            "vida": random.randint(20, 40),
            "vida_total": 40,
            "raio": random.uniform(3, 7),
            "cor": random.choice(CORES_POEIRA),
            "arrasto": 0.92,
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
alvo_largura = ALVO_DIAMETRO
alvo_altura = 15
# Reposiciona o alvo aleatoriamente na metade direita da tela, em cima do chão
alvo_x = random.randint(400, LARGURA - alvo_largura)
alvo_y = ALTURA - 50  # Alinhado com o topo do chão
pontos = 0

# --- FONTES DA HUD (estilo videogame) ---
fonte = pygame.font.SysFont("dejavusansmono", 17, bold=True)
fonte_rotulo = pygame.font.SysFont("dejavusansmono", 13, bold=True)
fonte_placar = pygame.font.SysFont("impact", 34)
fonte_tecla = pygame.font.SysFont("dejavusansmono", 14, bold=True)

# Cores auxiliares da HUD
CIANO = (80, 220, 255)
LARANJA = (255, 150, 60)
BRANCO_HUD = (235, 240, 245)


def desenha_texto_sombra(superficie, texto, fonte_usada, pos, cor, cor_sombra=(0, 0, 0), offset=2):
    """Renderiza um texto com uma sombra projetada, dando profundidade e um ar de HUD de jogo."""
    sombra = fonte_usada.render(texto, True, cor_sombra)
    principal = fonte_usada.render(texto, True, cor)
    superficie.blit(sombra, (pos[0] + offset, pos[1] + offset))
    superficie.blit(principal, pos)
    return principal.get_rect(topleft=pos)


def desenha_painel(superficie, rect, cor_fundo=(10, 14, 24, 160), cor_borda=(255, 255, 255, 70), raio=12):
    """Desenha um painel translúcido com cantos arredondados e borda sutil (estilo overlay de jogo)."""
    x, y, w, h = rect
    painel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(painel, cor_fundo, painel.get_rect(), border_radius=raio)
    pygame.draw.rect(painel, cor_borda, painel.get_rect(), width=2, border_radius=raio)
    superficie.blit(painel, (x, y))


def desenha_barra(superficie, pos, tamanho, valor, valor_max, cor_preenchido):
    """Desenha uma barra de progresso (estilo medidor de jogo) para um valor entre 0 e valor_max."""
    x, y = pos
    w, h = tamanho

    fundo = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(fundo, (255, 255, 255, 40), fundo.get_rect(), border_radius=h // 2)
    superficie.blit(fundo, (x, y))

    fracao = max(0.0, min(1.0, valor / valor_max))
    largura_preenchida = int(w * fracao)
    if largura_preenchida > 0:
        preenchido = pygame.Surface((largura_preenchida, h), pygame.SRCALPHA)
        pygame.draw.rect(preenchido, (*cor_preenchido, 230), preenchido.get_rect(), border_radius=h // 2)
        superficie.blit(preenchido, (x, y))

    borda = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(borda, (255, 255, 255, 100), borda.get_rect(), width=1, border_radius=h // 2)
    superficie.blit(borda, (x, y))


def desenha_tecla(superficie, texto, pos):
    """Desenha um pequeno badge estilo 'tecla do teclado', usado nas instruções da HUD."""
    padding_x, padding_y = 8, 5
    render = fonte_tecla.render(texto, True, BRANCO_HUD)
    w = render.get_width() + padding_x * 2
    h = render.get_height() + padding_y * 2
    badge = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(badge, (255, 255, 255, 35), badge.get_rect(), border_radius=6)
    pygame.draw.rect(badge, (255, 255, 255, 150), badge.get_rect(), width=1, border_radius=6)
    badge.blit(render, (padding_x, padding_y))
    superficie.blit(badge, pos)
    return w

# Loop Principal do Jogo
rodando = True
while rodando:
    # Desenha o Cenário (céu com nuvens e grama)
    atualiza_nuvens()
    desenha_cenario(tela)

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
            # Levanta poeira apenas quando a bola realmente toca o chão
            if bola_y >= ALTURA - 50:
                criar_particulas_poeira(bola_x, ALTURA - 50)
            em_movimento = False
            bola_x, bola_y = posicao_boca_canhao(angulo)

    # Atualiza as partículas do disparo (fumaça e faíscas)
    atualizar_particulas()

    # --- RENDERIZAÇÃO ---
    
    # Desenha o Alvo
    desenha_alvo(tela, alvo_x, alvo_y, alvo_largura, alvo_altura)
    
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
        
    # --- HUD: PAINEL DE TIRO (ângulo e velocidade com barras de medidor) ---
    desenha_painel(tela, (16, 16, 250, 108))

    desenha_texto_sombra(tela, "ÂNGULO", fonte_rotulo, (30, 26), CIANO)
    desenha_texto_sombra(tela, f"{angulo}°", fonte, (30, 42), BRANCO_HUD)
    desenha_barra(tela, (100, 48), (150, 10), angulo, 90, CIANO)

    desenha_texto_sombra(tela, "VELOCIDADE", fonte_rotulo, (30, 68), LARANJA)
    desenha_texto_sombra(tela, f"{velocidade:.1f}", fonte, (30, 84), BRANCO_HUD)
    desenha_barra(tela, (100, 90), (150, 10), velocidade, 30, LARANJA)

    # --- TEXTO DO STATUS DA RESISTÊNCIA ---
    status_ar = "ATIVADA" if resistencia_ativada else "DESATIVADA"
    cor_status = (110, 230, 140) if resistencia_ativada else (240, 90, 90)
    desenha_texto_sombra(tela, f"AR: {status_ar}", fonte_rotulo, (30, 108), cor_status)

    # --- HUD: PLACAR (canto superior direito) ---
    largura_placar = 190
    desenha_painel(tela, (LARGURA - largura_placar - 16, 16, largura_placar, 64))
    desenha_texto_sombra(tela, "PONTOS", fonte_rotulo, (LARGURA - largura_placar, 24), AMARELO)
    desenha_texto_sombra(
        tela, f"{pontos:03d}", fonte_placar,
        (LARGURA - largura_placar, 38), (255, 230, 90), offset=3,
    )

    # --- HUD: BARRA DE INSTRUÇÕES (rodapé) ---
    desenha_painel(tela, (16, ALTURA - 44, 420, 30), raio=8)
    x_tecla = 26
    x_tecla += desenha_tecla(tela, "ESPAÇO", (x_tecla, ALTURA - 40)) + 6
    tela.blit(fonte_rotulo.render("ATIRAR", True, BRANCO_HUD), (x_tecla, ALTURA - 36))
    x_tecla += 70
    x_tecla += desenha_tecla(tela, "R", (x_tecla, ALTURA - 40)) + 6
    tela.blit(fonte_rotulo.render("RESISTÊNCIA DO AR", True, BRANCO_HUD), (x_tecla, ALTURA - 36))

    pygame.display.flip()
    relogio.tick(60)
