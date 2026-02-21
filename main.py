import pygame
import random
import sys
import json
import os

# 1. INICIALIZAÇÃO
pygame.init()
pygame.mixer.init()

LARGURA, ALTURA, TAMANHO = 600, 600, 20
ecra = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake Game Pro")
relogio = pygame.time.Clock()

# Cores
PRETO, BRANCO, VERDE, AMARELO = (30, 30, 30), (250, 250, 250), (50, 200, 50), (255, 255, 0)
ARQUIVO_RECORDE = "recordes.json"


# 2. SISTEMA DE RECORDES
def ler_recordes():
    default = {"FACIL": [], "MEDIO": [], "DIFICIL": []}
    if not os.path.exists(ARQUIVO_RECORDE): return default
    try:
        with open(ARQUIVO_RECORDE, "r") as f:
            return json.load(f)
    except:
        return default


def salvar_recorde(nv, pts, nome):
    rds = ler_recordes()
    rds[nv].append({"nome": nome, "pontos": pts})
    rds[nv] = sorted(rds[nv], key=lambda x: x['pontos'], reverse=True)[:5]
    with open(ARQUIVO_RECORDE, "w") as f: json.dump(rds, f)


# 3. CARREGAMENTO DE ASSETS
def carregar(nome, s=(TAMANHO, TAMANHO)):
    try:
        return pygame.transform.scale(pygame.image.load(nome).convert_alpha(), s)
    except:
        return None


img_fundo = carregar("fundo.png", (LARGURA, ALTURA))
img_jogo = carregar("fundo_jogo.png", (LARGURA, ALTURA))
img_maca = carregar("maca.png", (25, 25))
img_pedra = carregar("pedra.png", (40, 40))
img_cabeca = carregar("cabeca.png", (35, 35))  # Cabeça imponente
img_corpo = carregar("corpo_vermelho.png", (20, 20))  # Corpo normal
img_explosao = carregar("explosao.png", (80, 80))
img_pocao = carregar("pocao.png", (25, 25))

try:
    pygame.mixer.music.load("musica.mp3")
    pygame.mixer.music.set_volume(0.1)
    som_comer = pygame.mixer.Sound("comer.mp3")
    som_morte = pygame.mixer.Sound("morreu.mp3")
except:
    som_comer = som_morte = None

# 4. FUNÇÕES DE INTERFACE
f_p = pygame.font.SysFont(None, 24);
f_g = pygame.font.SysFont(None, 40)


def desenhar_item_menu(texto, pos, sublinhar_index=0):
    letra_sub = texto[sublinhar_index]
    resto_antes = texto[:sublinhar_index]
    resto_depois = texto[sublinhar_index + 1:]

    # Renderização por partes para o sublinhado preciso
    img_antes = f_p.render(resto_antes, True, PRETO)
    img_letra = f_p.render(letra_sub, True, PRETO)
    img_depois = f_p.render(resto_depois, True, PRETO)

    x_offset = pos[0]
    ecra.blit(img_antes, (x_offset, pos[1]))
    x_offset += img_antes.get_width()

    ecra.blit(img_letra, (x_offset, pos[1]))
    pygame.draw.line(ecra, PRETO, (x_offset, pos[1] + 15), (x_offset + img_letra.get_width(), pos[1] + 15), 1)
    x_offset += img_letra.get_width()

    ecra.blit(img_depois, (x_offset, pos[1]))


def sortear_seguro(obstaculo):
    while True:
        pos = (random.randrange(0, LARGURA - TAMANHO, TAMANHO), random.randrange(100, ALTURA - TAMANHO, TAMANHO))
        if not (obstaculo[0] <= pos[0] < obstaculo[0] + 40 and obstaculo[1] <= pos[1] < obstaculo[1] + 40): return pos


# 5. VARIÁVEIS DE ESTADO
estado = "MENU";
nivel_atual = "FACIL";
drop_niveis = False;
drop_recordes = False
nivel_recorde_ver = "FACIL";
nome_input = "";
pontos = 0;
vel_atual = 10;
cobra = []
direcao = "PARADA";
dx = dy = 0;
pedra = (300, 200);
comida = (100, 100);
pocao = None;
invencivel = False;
t_inv = 0


def iniciar():
    global cobra, direcao, dx, dy, comida, pedra, pontos, vel_atual, estado, pocao, invencivel
    ecra.fill(PRETO);
    cobra = [(300, 300)];
    direcao = "PARADA";
    dx = dy = 0;
    pontos = 0;
    vel_atual = 10
    pedra = (random.randrange(100, 500, TAMANHO), random.randrange(150, 500, TAMANHO))
    comida = sortear_seguro(pedra);
    pocao = None;
    invencivel = False;
    estado = "JOGANDO"
    try:
        pygame.mixer.music.play(-1)
    except:
        pass


# 6. LOOP PRINCIPAL
while True:
    relogio.tick(vel_atual if estado == "JOGANDO" else 30)
    teclas = pygame.key.get_pressed()
    alt_pressionado = teclas[pygame.K_LALT] or teclas[pygame.K_RALT]

    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()

        # ESC para sair instantaneamente de qualquer tela
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            pygame.quit();
            sys.exit()

        if estado == "MENU":
            if e.type == pygame.KEYDOWN:
                if alt_pressionado and e.key == pygame.K_j:
                    drop_niveis = not drop_niveis; drop_recordes = False
                elif alt_pressionado and e.key == pygame.K_r:
                    drop_recordes = not drop_recordes; drop_niveis = False
                elif e.key == pygame.K_f:
                    if drop_niveis:
                        nivel_atual = "FACIL"; drop_niveis = False; iniciar()
                    elif drop_recordes:
                        nivel_recorde_ver = "FACIL"; drop_recordes = False; estado = "VER_RECORDE"
                elif e.key == pygame.K_m:
                    if drop_niveis:
                        nivel_atual = "MEDIO"; drop_niveis = False; iniciar()
                    elif drop_recordes:
                        nivel_recorde_ver = "MEDIO"; drop_recordes = False; estado = "VER_RECORDE"
                elif e.key == pygame.K_d:
                    if drop_niveis:
                        nivel_atual = "DIFICIL"; drop_niveis = False; iniciar()
                    elif drop_recordes:
                        nivel_recorde_ver = "DIFICIL"; drop_recordes = False; estado = "VER_RECORDE"

            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if 10 <= mx <= 110 and 0 <= my <= 35:
                    drop_niveis = not drop_niveis; drop_recordes = False
                elif 120 <= mx <= 230 and 0 <= my <= 35:
                    drop_recordes = not drop_recordes; drop_niveis = False
                elif drop_niveis and 10 <= mx <= 110 and 35 <= my <= 140:
                    nivel_atual = ["FACIL", "MEDIO", "DIFICIL"][(my - 35) // 35];
                    drop_niveis = False;
                    iniciar()
                elif drop_recordes and 120 <= mx <= 230 and 35 <= my <= 140:
                    nivel_recorde_ver = ["FACIL", "MEDIO", "DIFICIL"][(my - 35) // 35];
                    drop_recordes = False;
                    estado = "VER_RECORDE"

        elif estado == "VER_RECORDE":
            # Aguarda comando para voltar
            if e.type == pygame.KEYDOWN:
                if e.key in [pygame.K_SPACE, pygame.K_RETURN]: estado = "MENU"
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if 0 <= my <= 35: estado = "MENU"  # Clicar na barra do topo volta

        elif estado == "DIGITAR_NOME" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN and nome_input:
                salvar_recorde(nivel_atual, pontos, nome_input);
                nivel_recorde_ver = nivel_atual;
                estado = "VER_RECORDE"
            elif e.key == pygame.K_BACKSPACE:
                nome_input = nome_input[:-1]
            else:
                nome_input += e.unicode if len(nome_input) < 12 else ""

        elif estado == "JOGANDO" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_UP and direcao != "BAIXO":
                dx, dy, direcao = 0, -TAMANHO, "CIMA"
            elif e.key == pygame.K_DOWN and direcao != "CIMA":
                dx, dy, direcao = 0, TAMANHO, "BAIXO"
            elif e.key == pygame.K_LEFT and direcao != "DIREITA":
                dx, dy, direcao = -TAMANHO, 0, "ESQUERDA"
            elif e.key == pygame.K_RIGHT and direcao != "ESQUERDA":
                dx, dy, direcao = TAMANHO, 0, "DIREITA"

    # 7. PROCESSAMENTO E MOVIMENTO
    if estado == "JOGANDO" and direcao != "PARADA":
        nx, ny = (cobra[0][0] + dx) % LARGURA, (cobra[0][1] + dy)
        if ny < 80:
            ny = ALTURA - TAMANHO
        elif ny >= ALTURA:
            ny = 80
        nova = (nx, ny)

        hit_corpo = nova in cobra
        hit_pedra = (pedra[0] <= nx < pedra[0] + 40 and pedra[1] <= ny < pedra[1] + 40)

        if (hit_corpo or hit_pedra) and not invencivel:
            if som_morte: som_morte.play()
            ecra.fill(PRETO)
            if img_jogo: ecra.blit(img_jogo, (0, 0))
            if hit_pedra and img_explosao: ecra.blit(img_explosao, (nx - 30, ny - 30))
            pygame.display.flip();
            pygame.time.delay(800)
            rds = ler_recordes().get(nivel_atual, [])
            if len(rds) < 5 or pontos > rds[-1]['pontos']:
                nome_input = "";
                estado = "DIGITAR_NOME"
            else:
                nivel_recorde_ver = nivel_atual;
                estado = "VER_RECORDE"
        else:
            cobra.insert(0, nova)
            if nx == comida[0] and ny == comida[1]:
                if som_comer: som_comer.play()
                pontos += 1;
                comida = sortear_seguro(pedra)
                if random.random() < 0.10: pocao = sortear_seguro(pedra)
                if nivel_atual == "MEDIO":
                    vel_atual = 10 + (pontos // 5)
                elif nivel_atual == "DIFICIL":
                    vel_atual = 10 + (pontos // 3)
            elif pocao and nx == pocao[0] and ny == pocao[1]:
                invencivel = True;
                t_inv = pygame.time.get_ticks();
                pocao = None
            else:
                cobra.pop()
            if invencivel and pygame.time.get_ticks() - t_inv > 5000: invencivel = False

    # 8. RENDERIZAÇÃO
    ecra.fill(PRETO)

    if estado == "MENU":
        if img_fundo: ecra.blit(img_fundo, (0, 0))
        pygame.draw.rect(ecra, BRANCO, (0, 0, LARGURA, 35))
        desenhar_item_menu("Jogar", (15, 10), 0)
        desenhar_item_menu("Record", (130, 10), 0)
        if drop_niveis:
            for i, n in enumerate(["(F) Fácil", "(M) Médio", "(D) Difícil"]):
                pygame.draw.rect(ecra, BRANCO, (10, 35 + i * 35, 130, 35))
                ecra.blit(f_p.render(n, True, PRETO), (15, 45 + i * 35))
        if drop_recordes:
            for i, n in enumerate(["(F) Fácil", "(M) Médio", "(D) Difícil"]):
                pygame.draw.rect(ecra, BRANCO, (120, 35 + i * 35, 130, 35))
                ecra.blit(f_p.render(n, True, PRETO), (125, 45 + i * 35))

    elif estado == "JOGANDO":
        if img_jogo: ecra.blit(img_jogo, (0, 0))
        ecra.blit(img_pedra, pedra);
        ecra.blit(img_maca, (comida[0] - 2, comida[1] - 2))
        if pocao: ecra.blit(img_pocao, (pocao[0] - 2, pocao[1] - 2))
        for i, (px, py) in enumerate(cobra):
            if invencivel and (pygame.time.get_ticks() // 100) % 2 == 0: continue
            if i == 0:
                r = 90 if direcao == "CIMA" else 270 if direcao == "BAIXO" else 180 if direcao == "ESQUERDA" else 0
                ecra.blit(pygame.transform.rotate(img_cabeca, r), (px - 7, py - 7))
            else:
                ecra.blit(img_corpo, (px, py))
        pygame.draw.rect(ecra, PRETO, (0, 0, LARGURA, 60))
        ecra.blit(f_p.render(f"Maçãs: {pontos} | Nível: {nivel_atual}", True, BRANCO), (20, 20))

    elif estado == "VER_RECORDE":
        # Barra branca contínua no topo
        pygame.draw.rect(ecra, BRANCO, (0, 0, LARGURA, 35))
        desenhar_item_menu("< Voltar (Esc)", (15, 10), 9)

        titulo = f_g.render(f"RECORDE: {nivel_recorde_ver}", True, AMARELO)
        ecra.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 80))

        rds = ler_recordes().get(nivel_recorde_ver, [])
        for i, r in enumerate(rds):
            txt = f_p.render(f"{i + 1}. {r['nome']} - {r['pontos']} pts", True, BRANCO)
            ecra.blit(txt, (LARGURA // 2 - 100, 160 + i * 40))

    elif estado == "DIGITAR_NOME":
        ecra.blit(f_g.render("NOVO RECORDE!", True, AMARELO), (180, 150))
        ecra.blit(f_g.render(nome_input, True, VERDE), (160, 265))

    pygame.display.flip()