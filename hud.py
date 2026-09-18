"""HUD do jogo: painéis translúcidos, texto com sombra, barras de medidor e placar,
com um estilo mais próximo de um videogame de verdade."""
import pygame

CIANO = (80, 220, 255)
LARANJA = (255, 150, 60)
AMARELO = (255, 215, 0)
BRANCO_HUD = (235, 240, 245)


class HUD:
    """Desenha todos os elementos de interface sobre a cena do jogo."""

    def __init__(self):
        self.fonte = pygame.font.SysFont("dejavusansmono", 17, bold=True)
        self.fonte_rotulo = pygame.font.SysFont("dejavusansmono", 13, bold=True)
        self.fonte_placar = pygame.font.SysFont("impact", 34)
        self.fonte_tecla = pygame.font.SysFont("dejavusansmono", 14, bold=True)

    # --- utilidades genéricas de desenho ---
    def _texto_sombra(self, superficie, texto, fonte, pos, cor, cor_sombra=(0, 0, 0), offset=2):
        """Renderiza um texto com uma sombra projetada, dando profundidade e um ar de HUD de jogo."""
        sombra = fonte.render(texto, True, cor_sombra)
        principal = fonte.render(texto, True, cor)
        superficie.blit(sombra, (pos[0] + offset, pos[1] + offset))
        superficie.blit(principal, pos)

    def _painel(self, superficie, rect, cor_fundo=(10, 14, 24, 160), cor_borda=(255, 255, 255, 70), raio=12):
        """Desenha um painel translúcido com cantos arredondados e borda sutil."""
        x, y, w, h = rect
        painel = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(painel, cor_fundo, painel.get_rect(), border_radius=raio)
        pygame.draw.rect(painel, cor_borda, painel.get_rect(), width=2, border_radius=raio)
        superficie.blit(painel, (x, y))

    def _barra(self, superficie, pos, tamanho, valor, valor_max, cor_preenchido):
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

    def _tecla(self, superficie, texto, pos):
        """Desenha um pequeno badge estilo 'tecla do teclado', usado nas instruções da HUD."""
        padding_x, padding_y = 8, 5
        render = self.fonte_tecla.render(texto, True, BRANCO_HUD)
        w = render.get_width() + padding_x * 2
        h = render.get_height() + padding_y * 2
        badge = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(badge, (255, 255, 255, 35), badge.get_rect(), border_radius=6)
        pygame.draw.rect(badge, (255, 255, 255, 150), badge.get_rect(), width=1, border_radius=6)
        badge.blit(render, (padding_x, padding_y))
        superficie.blit(badge, pos)
        return w

    # --- HUD completa ---
    def desenhar(self, superficie, largura, altura, angulo, velocidade, resistencia_ativada, pontos):
        # Painel de tiro (ângulo e velocidade com barras de medidor)
        self._painel(superficie, (16, 16, 250, 108))

        self._texto_sombra(superficie, "ÂNGULO", self.fonte_rotulo, (30, 26), CIANO)
        self._texto_sombra(superficie, f"{angulo}°", self.fonte, (30, 42), BRANCO_HUD)
        self._barra(superficie, (100, 48), (150, 10), angulo, 90, CIANO)

        self._texto_sombra(superficie, "VELOCIDADE", self.fonte_rotulo, (30, 68), LARANJA)
        self._texto_sombra(superficie, f"{velocidade:.1f}", self.fonte, (30, 84), BRANCO_HUD)
        self._barra(superficie, (100, 90), (150, 10), velocidade, 30, LARANJA)

        status_ar = "ATIVADA" if resistencia_ativada else "DESATIVADA"
        cor_status = (110, 230, 140) if resistencia_ativada else (240, 90, 90)
        self._texto_sombra(superficie, f"AR: {status_ar}", self.fonte_rotulo, (30, 108), cor_status)

        # Placar (canto superior direito)
        largura_placar = 190
        self._painel(superficie, (largura - largura_placar - 16, 16, largura_placar, 64))
        self._texto_sombra(superficie, "PONTOS", self.fonte_rotulo, (largura - largura_placar, 24), AMARELO)
        self._texto_sombra(
            superficie, f"{pontos:03d}", self.fonte_placar,
            (largura - largura_placar, 38), (255, 230, 90), offset=3,
        )

        # Barra de instruções (rodapé)
        self._painel(superficie, (16, altura - 44, 420, 30), raio=8)
        x_tecla = 26
        x_tecla += self._tecla(superficie, "ESPAÇO", (x_tecla, altura - 40)) + 6
        superficie.blit(self.fonte_rotulo.render("ATIRAR", True, BRANCO_HUD), (x_tecla, altura - 36))
        x_tecla += 70
        x_tecla += self._tecla(superficie, "R", (x_tecla, altura - 40)) + 6
        superficie.blit(
            self.fonte_rotulo.render("RESISTÊNCIA DO AR", True, BRANCO_HUD), (x_tecla, altura - 36)
        )
