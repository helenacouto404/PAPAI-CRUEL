import math
import os
import random
from collections import deque

import pygame

from PPlay.keyboard import Keyboard
from PPlay.window import Window
from PPlay.sprite import Sprite
from PPlay.mouse import Mouse
from PPlay.camera import Camera
from fonte_pixel import renderizar, largura as largura_texto
from PPlay.sound import Sound, Music, SoundManager

SoundManager.inicializar()
SoundManager.set_music_volume(55)
SoundManager.set_sfx_volume(90)
_sons = {}
_musica_atual = [None]
_camadas = []
_camadas_som = []
_camadas_nivel = [None]
_vol_tensao = [0.0]
mudo = False


def som(nome):
    if nome not in _sons:
        _sons[nome] = Sound(os.path.join("sons", nome + ".wav"))
    return _sons[nome]


def tocar(nome):
    s = som(nome)
    s.set_volume(0 if mudo else 90)
    s.play()


def tocar_musica(nome, repete=True):
    if _musica_atual[0] == nome:
        return
    _musica_atual[0] = nome
    if nome is None:
        pygame.mixer.music.fadeout(400)
        return
    Music(os.path.join("sons", "musica_" + nome + ".wav")).play(loops=-1 if repete else 0, fade_in_ms=600)
    pygame.mixer.music.set_volume(0 if mudo else 0.55)


def musica_desejada():
    if estado == "MENU" or estado == "MAPA":
        return "menu", True
    if estado == "VITORIA":
        return "vitoria", False
    if estado == "DERROTA":
        return "derrota", False
    return "menu", True


def iniciar_camadas():
    parar_camadas()
    base = pygame.mixer.Sound(os.path.join("sons", "natal_base.wav"))
    tensao = pygame.mixer.Sound(os.path.join("sons", "natal_tensao_nivel" + str(nivel_atual + 1) + ".wav"))
    _camadas[:] = [base.play(loops=-1), tensao.play(loops=-1)]
    _camadas_som[:] = [base, tensao]
    _camadas_nivel[0] = nivel_atual
    _vol_tensao[0] = 0.0


def parar_camadas():
    for c in _camadas:
        if c is not None:
            c.stop()
    _camadas[:] = []
    _camadas_som[:] = []
    _camadas_nivel[0] = None


def atualizar_tensao(dt):
    if len(_camadas) < 2:
        return
    if subterraneo:
        alvo = 0.0
    else:
        dist = math.hypot(boss_cx - (nico_x + NICO_W / 2), boss_cy - (nico_y + NICO_H / 2))
        prox = max(0.0, min(1.0, 1.0 - dist / (TAMANHO_TILE * 6)))
        alvo = prox ** 1.5
    _vol_tensao[0] += (alvo - _vol_tensao[0]) * min(1.0, dt * 3.0)
    ganho = 0.0 if mudo else 1.0
    _camadas[0].set_volume(0.0 if subterraneo else 0.4 * ganho)
    _camadas[1].set_volume(_vol_tensao[0] * ganho)


def atualizar_audio(dt):
    global mudo
    if apertou("M"):
        mudo = not mudo
        pygame.mixer.music.set_volume(0 if mudo else 0.55)
    if estado == "JOGO":
        if not _camadas or _camadas_nivel[0] != nivel_atual:
            iniciar_camadas()
        if subterraneo:
            tocar_musica("caverna", True)
        else:
            tocar_musica(None)
        atualizar_tensao(dt)
    else:
        parar_camadas()
        nome, repete = musica_desejada()
        tocar_musica(nome, repete)


janela = Window(1200, 700)
janela.set_title("Papai Cruel - Noite de Caos")
mouse = Mouse()
teclado = Keyboard()

TAMANHO_TILE = 64
MAGIA_INICIAL = 100.0
DRENO_MAGIA = 2.0
PENALIDADE_CAPTURA = 20
RECUPERA_FRAGMENTO = 30
MAGIA_MOEDA = 5
MAGIA_POCAO = 40
PROTECAO_APOS_CAPTURA = 2.0
TEMPO_MENSAGEM = 2.5
RAIO_PORTA = 80
RAIO_COLETA = 40
VEL_NICO = 300
HITBOX_NICO = (44, 46)
HITBOX_PAPAI = (56, 56)
HITBOX_ELFO = (36, 36)
VEL_ELFO = 60
VEL_ELFO_FUGA = 150
RAIO_MEDO_ELFO = 260
FATOR_CACA_ELFO = 0.9
PAUSA_APOS_PEGAR_ELFO = 1.5
RAIO_PASSEIO_ELFO = 5
ALCANCE_CACA_ELFO = 600
ALCANCE_ESPERA_PAPAI = 0.35
VEL_ANIM_NICO_ANDAR = 0.10
VEL_ANIM_NICO_PARADO = 0.20
VEL_ANIM_PAPAI = 0.09
VEL_ANIM_ELFO_ANDAR = 0.14
VEL_ANIM_ELFO_PARADO = 0.30
VEL_ANIM_ELFO_MORTE = 0.12
DURACAO_MORTE_ELFO = 0.48
NEVE_QUANTIDADE = 90
ESCURIDAO_ALFA = 245
BLOQUEANTES = set("WTRXYVCNHQLZ&")
DIRECOES = ("down", "left", "right", "up")

NIVEIS = [
    {
        "nome": "Pátio de Neve",
        "tema": "dia",
        "vel_patrulha": 110,
        "vel_perseguicao": 170,
        "alcance_tiles": 5,
        "rota": [(12, 3), (26, 3), (26, 20), (12, 20)],
        "mapa": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWW.W...W....W.......W...WAAAWWWAW",
            "WW.....WW...T...T....T...T...T.WAEAAWAAW",
            "WW.K....W..........J..M........WAAAAAAWW",
            "WW.E....D..M.....b.............AAMAAAAWW",
            "WW....Q.W......J..........E....WAAAAFAWW",
            "WWWWW...W...EG.........G....J..WWAAAAAWW",
            "WWWWWWWWW..........T.J.........WAAAAAAAW",
            "WWWWWWWWW.L.............T.....VWARAWAWAW",
            "WWWWWWWWW...........E.....b....WWWWWWWWW",
            "WWWWWWWWWY.T..Q.V..............W.WW....W",
            "WWWWWWWWW..................G..WW......WW",
            "WWWWWWWWWW.....M..P.Z..Y....M..WW..bO.WW",
            "WWWWWWWWWW.T.............Z.....W..K....W",
            "WWWWWWWWW.....G......J.......b.W.....WWW",
            "WWWWWWWWWW................E....W..M...WW",
            "WWWWWWWWW..........T...OT...........H..W",
            "WWWW.W..W..Q.b.................W.C....WW",
            "WWW.....W.......E..........Z...W....E..W",
            "WW...F..D...........G........M.W.......W",
            "WW.E....W.....M............R...W.G.S...W",
            "WW...W.WW..T...T..N..T.W.T...T.W.......W",
            "WWWWWWWWWW.............W.......W..WWWW.W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "zona": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWW.W...W....W.......W...WAAAWWWAW",
            "WW.....WW......................WAAAAWAAW",
            "WW......W......................WAAAAAAWW",
            "WW.............................AAAAAAAWW",
            "WW......W......................WAAAAAAWW",
            "WWWWW...W......................WWAAAAAWW",
            "WWWWWWWWW......................WAAAAAAAW",
            "WWWWWWWWW......................WAAAWAWAW",
            "WWWWWWWWW......................WWWWWWWWW",
            "WWWWWWWWW......................W.WW....W",
            "WWWWWWWWW.....................WW......WW",
            "WWWWWWWWWW.....................WW.....WW",
            "WWWWWWWWWW.....................W.......W",
            "WWWWWWWWW......................W.....WWW",
            "WWWWWWWWWW.....................W......WW",
            "WWWWWWWWW..............................W",
            "WWWW.W..W......................W......WW",
            "WWW.....W......................W.......W",
            "WW.............................W.......W",
            "WW......W......................W.......W",
            "WW...W.WW..............W.......W.......W",
            "WWWWWWWWWW.............W.......W..WWWW.W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "subs": [
        ],
    },
    {
        "nome": "Fábrica de Brinquedos",
        "tema": "dia",
        "vel_patrulha": 120,
        "vel_perseguicao": 185,
        "alcance_tiles": 5,
        "rota": [(12, 4), (26, 4), (26, 14), (12, 14)],
        "mapa": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WW...W...W.......W........WWW.WWWWWWAWWW",
            "WW.E.....W.M.G......V...G.....WWWAAAAAAW",
            "WW..K....W.........M.........WWWWWAAFEAW",
            "WWW......D......J.....Q.........AAAAAAAW",
            "WW.......W.N..E...............WWWAAAAAAW",
            "WW.......W.....K......P.....N.WWWWAAAWWW",
            "WWW..W.M.W........G...........WWWAAAAAAW",
            "WW..WW...W.Y.Z.............M.WWWWWAWWWAW",
            "WWWWWWWWWW...............J....WWWWWWWWWW",
            "WWWWWWWWWWW........J..E......WWWWWWWWWWW",
            "WWWWWWWWWW..E.J.........Q.G..WWWWBOBWBBW",
            "WWBBWBBBBWW......Q...O.......WWWWBBBBBBW",
            "WWXBBBBXBWW....M..............WWWBKBBBBW",
            "WWBBBBBBBW.........Z........Y.WWWBBBBBBW",
            "WWBEBBBBBW...C.........M......WWWWBBBBWW",
            "WWBBBBBBBD........E...........D..BBBBBBW",
            "WWBBXBBBBW...............RE...WWWWBBBLBW",
            "WWBBBBBHBWW.S..Z..............WWWBBBBBBW",
            "WWBFBBBBBWW......W..V...E...G.WWWBMBEFBW",
            "WWBBBWWBWW..W.G.WWW...........WWWBBBBBBW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "zona": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WW...W...W.......W........WWW.WWWWWWAWWW",
            "WW.......W....................WWWAAAAAAW",
            "WW.......W...................WWWWWAAAAAW",
            "WWW.............................AAAAAAAW",
            "WW.......W....................WWWAAAAAAW",
            "WW.......W....................WWWWAAAWWW",
            "WWW..W...W....................WWWAAAAAAW",
            "WW..WW...W...................WWWWWAWWWAW",
            "WWWWWWWWWW....................WWWWWWWWWW",
            "WWWWWWWWWWW..................WWWWWWWWWWW",
            "WWWWWWWWWW...................WWWWBBBWBBW",
            "WWBBWBBBBWW..................WWWWBBBBBBW",
            "WWBBBBBBBWW...................WWWBBBBBBW",
            "WWBBBBBBBW....................WWWBBBBBBW",
            "WWBBBBBBBW....................WWWWBBBBWW",
            "WWBBBBBBB........................BBBBBBW",
            "WWBBBBBBBW....................WWWWBBBBBW",
            "WWBBBBBBBWW...................WWWBBBBBBW",
            "WWBBBBBBBWW......W............WWWBBBBBBW",
            "WWBBBWWBWW..W...WWW...........WWWBBBBBBW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "subs": [
        ],
    },
    {
        "nome": "Oficina do Yeti",
        "tema": "dia",
        "vel_patrulha": 130,
        "vel_perseguicao": 200,
        "alcance_tiles": 6,
        "rota": [(20, 3), (20, 20), (4, 20), (4, 3)],
        "mapa": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWBBBWWBWWBBBBBWBWBBBWBBWWWAAAAWWWAAAAW",
            "WWWBBBBBBBBBBEBBBBBBBBBBBBBWWAMAWAAAAEAW",
            "WWBBXBMBXBBBBBBBMBBBBBBCBBBWAAAAAAAJAAAW",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBDAAAAAFAAAAAW",
            "WWWBBBBBBBBZBBZBBBBBPBBBMBBWAAAAAAAAAAWW",
            "WWWWBBBBBBBBBBBBBNBBBBBBBBBWAAAAAAAAAAAW",
            "WWBBBBBBEBBBBBBBBBBBBBXBBBWWAEAAWAAAMAAW",
            "WWWBBBNBBBBBBBBBBBBBBBBBBBBWAAAWWWWAAAWW",
            "WWWBEBBBBBBBBBBBBBOBBBBBBQBWWWWWWWWWWWWW",
            "WWWBBBBBBMBBJBUBBBBBBBBBBBBWWWWWWWWWWWWW",
            "WWWWBBBBBBBBBBBBBBBBEBBBBBWW...G.M.W.W.W",
            "WWBBBBBQBBBBBBBBZBBBBBBBBBBW...........W",
            "WWBXBHBBBBBBBBBBBBEBBBBBXBBW..K........W",
            "WWBBBBBBBEBBBBBBLBBBBBBBBBBW........O..W",
            "WWWBMBBBBBBBJBBBBBBBMBBBBBBD.......G...W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBSBBBBBBBBBBBBBBBEBZBBW.J...Y...J.W",
            "WWBBBBBBBBCBBBBBBBXBBBBBBBWW...........W",
            "WWBBBKBBBBBBBBMBBBBBBBBBBBBW..G.....EF.W",
            "WWBBBBBWBBWWWBBBBWWBBBBWBBWWW...W.W....W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "zona": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWBBBWWBWWBBBBBWBWBBBWBBWWWAAAAWWWAAAAW",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBBWWAAAWAAAAAAW",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBWAAAAAAAAAAAW",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBAAAAAAAAAAAAW",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBBWAAAAAAAAAAWW",
            "WWWWBBBBBBBBBBBBBBBBBBBBBBBWAAAAAAAAAAAW",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBWWAAAAWAAAAAAW",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBBWAAAWWWWAAAWW",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBBWWWWWWWWWWWWW",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBBWWWWWWWWWWWWW",
            "WWWWBBBBBBBBBBBBBBBBBBBBBBWW.......W.W.W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWWBBBBBBBBBBBBBBBBBBBBBBBB............W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBWW...........W",
            "WWBBBBBBBBBBBBBBBBBBBBBBBBBW...........W",
            "WWBBBBBWBBWWWBBBBWWBBBBWBBWWW...W.W....W",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "subs": [
            {
                "mapa": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWBRBWWWWWWBBBBBBBBBBWBBBWW",
                    "WWWBBBVBBWWWWWWBMBNBBXBBBBMBWW",
                    "WWBBUBBBBBBMBBBBBGBGBBBBBBBBWW",
                    "WWBJBBBBBWBBBWBBBBBBBBBBBKBWWW",
                    "WWBVBBBBBWWWWWBBBCBBMBBBBBBBWW",
                    "WWBBBWBWWWWWWWBXBBBBBQBBBBXBWW",
                    "WWWWBWWWWWWWWWBBBWWBBBBWBBBBWW",
                    "WWWWBWWWWWWWWWWWWWBBWWWWWWWWWW",
                    "WWWWWBWWWWWWWWWWWWMBWWWWWWWWWW",
                    "WWWWWBBBXBBBBWBBBBBBWBBBRBBBWW",
                    "WWBBBBBMBBBXBBBCJBBBBBMBBBYBWW",
                    "WWBMBBBBBBQBMBBBBBBBBJBBBFBBWW",
                    "WWBBOBWBWBBBBVBBMBBBXBBBVBBWWW",
                    "WWXBBBWBWBWWBBRBBBBBBBBBBBWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
                "zona": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWBBBWWWWWWBBBBBBBBBBWBBBWW",
                    "WWWBBBBBBWWWWWWBBBBBBBBBBBBBWW",
                    "WWBBBBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWBBBBBBBWBBBWBBBBBBBBBBBBBWWW",
                    "WWBBBBBBBWWWWWBBBBBBBBBBBBBBWW",
                    "WWBBBWBWWWWWWWBBBBBBBBBBBBBBWW",
                    "WWWWBWWWWWWWWWBBBWWBBBBWBBBBWW",
                    "WWWWBWWWWWWWWWWWWWBBWWWWWWWWWW",
                    "WWWWWBWWWWWWWWWWWWBBWWWWWWWWWW",
                    "WWWWWBBBBBBBBWBBBBBBWBBBBBBBWW",
                    "WWBBBBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWBBBBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWBBBBWBWBBBBBBBBBBBBBBBBBBWWW",
                    "WWBBBBWBWBWWBBBBBBBBBBBBBBWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
            },
        ],
    },
    {
        "nome": "Biblioteca do Crepúsculo",
        "tema": "tarde",
        "vel_patrulha": 140,
        "vel_perseguicao": 215,
        "alcance_tiles": 6,
        "rota": [(18, 12), (34, 12), (34, 26), (18, 26)],
        "mapa": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWW........WWW.....WWW.W..W.....WW....WWW.WW.W..WWWW",
            "WWW......M.WWW...M........W.....W...M...........WWWW",
            "WW..F........D..........E.....E...............K.WWWW",
            "WW..........WW..............M....Z......E.J.....WWWW",
            "WW......E...WWW...........W........J........M....WWW",
            "WW..L......WWW..W.....WWW.WW..W.......WW.......W.WWW",
            "WWW.........WWWWWWWW..WWWWWWWWW..WWWWWWWWWWWWWWWWWWW",
            "WW..M......WWWWWWWWW..WWWWWWWWW..WWWWWWWWWWWWWWWWWWW",
            "WW.........WWWWWWWWW.WW....WW....WWWWWWWWBBBBWBBBBWW",
            "WWW.........WWWWW........T....M.....WWWWWBBBBBBBMBWW",
            "WW....E..Q..WWWW..M....L.............WWWBBNBEBBBBBWW",
            "WW.........WWWWWW................T...WWWWBBBBBBBWWWW",
            "WWW........WWWWWW...E.....P........Q.WWWBBBMBBBBBBWW",
            "WW...K......WWWW.......................DBZBBBBBBBBWW",
            "WWW.....J.O.WWWW.T...............J...WWWBBBBBBBBBWWW",
            "WWW.........WWWW.....Z......J......Q.WWWBBEBBBBFBWWW",
            "WW..W....WW.WWWWW.......J.......E....WWWBOBBBBBBBBWW",
            "WWWWWWWWWWWWWWWW..............Q......WWWBBBWBBWBWWWW",
            "WWWWWWWWWWWWWWWW...N................WWWWWWWWW.WWWWWW",
            "WWAAAAAAWAATAWWW.J....Z...U..Q....T..WWWWWWWW.WWWWWW",
            "WWATAAAAAAAAAWWW...T...............M.WWWWWWWWDWWWWWW",
            "WWAAAAZAEAAAWWWWW.............N......WWWWWAAAAAAAAWW",
            "WWWAAAAAAACAAWWWW................Z..WWWWAAAXAAAAXAWW",
            "WWWAASAAAAAAA.........E.J..C.........WWWAAMAAAAAAAWW",
            "WWWAAAAJAAAAA..................Z..E.WWWWAAAAAAAAWWWW",
            "WWAAAAAAAKAAAWWWW.M......N..O.......WWWWAAAAAA&AAAWW",
            "WWAHAWAAAAAMAWWWW......W......W.WW...WWWAXAAWAAAMAWW",
            "WWAAAWAAWWAAAWWWWWWWWWWWWWWWWWWWWWWWWWWWAAAWWWWAAAWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "zona": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWW........WWW.....WWW.W..W.....WW....WWW.WW.W..WWWW",
            "WWW........WWW............W.....W...............WWWW",
            "WW..............................................WWWW",
            "WW..........WW..................................WWWW",
            "WW..........WWW...........W......................WWW",
            "WW.........WWW..W.....WWW.WW..W.......WW.......W.WWW",
            "WWW.........WWWWWWWW..WWWWWWWWW..WWWWWWWWWWWWWWWWWWW",
            "WW.........WWWWWWWWW..WWWWWWWWW..WWWWWWWWWWWWWWWWWWW",
            "WW.........WWWWWWWWW.WW....WW....WWWWWWWWBBBBWBBBBWW",
            "WWW.........WWWWW...................WWWWWBBBBBBBBBWW",
            "WW..........WWWW.....................WWWBBBBBBBBBBWW",
            "WW.........WWWWWW....................WWWWBBBBBBBWWWW",
            "WWW........WWWWWW....................WWWBBBBBBBBBBWW",
            "WW..........WWWW........................BBBBBBBBBBWW",
            "WWW.........WWWW.....................WWWBBBBBBBBBWWW",
            "WWW.........WWWW.....................WWWBBBBBBBBBWWW",
            "WW..W....WW.WWWWW....................WWWBBBBBBBBBBWW",
            "WWWWWWWWWWWWWWWW.....................WWWBBBWBBWBWWWW",
            "WWWWWWWWWWWWWWWW....................WWWWWWWWW.WWWWWW",
            "WWAAAAAAWAAAAWWW.....................WWWWWWWW.WWWWWW",
            "WWAAAAAAAAAAAWWW.....................WWWWWWWWAWWWWWW",
            "WWAAAAAAAAAAWWWWW....................WWWWWAAAAAAAAWW",
            "WWWAAAAAAAAAAWWWW...................WWWWAAAAAAAAAAWW",
            "WWWAAAAAAAAAA........................WWWAAAAAAAAAAWW",
            "WWWAAAAAAAAAA.......................WWWWAAAAAAAAWWWW",
            "WWAAAAAAAAAAAWWWW...................WWWWAAAAAAAAAAWW",
            "WWAAAWAAAAAAAWWWW......W......W.WW...WWWAAAAWAAAAAWW",
            "WWAAAWAAWWAAAWWWWWWWWWWWWWWWWWWWWWWWWWWWAAAWWWWAAAWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "subs": [
            {
                "mapa": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWBBRBBWWWWWWBBBBBBBBBBWWWBBBWW",
                    "WWWBBBVBBBWWWWWWWBMBBBNBXBWBBBMBWW",
                    "WWWBUBBBBWWBMBWWWBBBBGBGBBWWBBBBWW",
                    "WWBBBBBBBBBBBBBBBBBBCBBBBWWBBBBWWW",
                    "WWBJBBBBBBWWWWWWWWBBBBBBBBWBBBBBWW",
                    "WWBBBBBBBBWWWWWWBBBBBBBMBBWWBBBWWW",
                    "WWWBBBWWWWWWWWWWBXBBBBBBBBWWBBBWWW",
                    "WWWWBBWWWWWWWWWWBBBWBBWWWBWWBKBWWW",
                    "WWWWWBWWWWWWWWWWWWWWBWWWWWWWBBBBWW",
                    "WWWWWBWWWWWWWWWWWWWWBWWWWWWWBBXBWW",
                    "WWWWWWWWWWWWWWWWWWWWBWWWWWWWBBBBWW",
                    "WWWWBWBWWWWBBWWBBWWWBBWWBBBBBBWWWW",
                    "WWBBBBBBBBWWBWBBBBBBBBBBBBMBYBBBWW",
                    "WWWBBBBBMBBBBBBBCBOBBBBBBBBBBBWWWW",
                    "WWWBBBBBBBBBBBMBBBBBBBBBBBBBBBBWWW",
                    "WWBBMBBBBBBBBVBBBWBJBBMBBBBBBFBWWW",
                    "WWBXBBBBWBBBXBBWWWBBBBBBBRBVBBBBWW",
                    "WWBBBWBBWWBBBBBWWWWWWWWWBBBBBWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
                "zona": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWBBBBBWWWWWWBBBBBBBBBBWWWBBBWW",
                    "WWWBBBBBBBWWWWWWWBBBBBBBBBWBBBBBWW",
                    "WWWBBBBBBWWBBBWWWBBBBBBBBBWWBBBBWW",
                    "WWBBBBBBBBBBBBBBBBBBBBBBBWWBBBBWWW",
                    "WWBBBBBBBBWWWWWWWWBBBBBBBBWBBBBBWW",
                    "WWBBBBBBBBWWWWWWBBBBBBBBBBWWBBBWWW",
                    "WWWBBBWWWWWWWWWWBBBBBBBBBBWWBBBWWW",
                    "WWWWBBWWWWWWWWWWBBBWBBWWWBWWBBBWWW",
                    "WWWWWBWWWWWWWWWWWWWWBWWWWWWWBBBBWW",
                    "WWWWWBWWWWWWWWWWWWWWBWWWWWWWBBBBWW",
                    "WWWWWWWWWWWWWWWWWWWWBWWWWWWWBBBBWW",
                    "WWWWBWBWWWWBBWWBBWWWBBWWBBBBBBWWWW",
                    "WWBBBBBBBBWWBWBBBBBBBBBBBBBBBBBBWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBBBBWWWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWBBBBBBBBBBBBBBBWBBBBBBBBBBBBBWWW",
                    "WWBBBBBBWBBBBBBWWWBBBBBBBBBBBBBBWW",
                    "WWBBBWBBWWBBBBBWWWWWWWWWBBBBBWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
            },
        ],
    },
    {
        "nome": "Noite Feliz",
        "tema": "noite",
        "vel_patrulha": 150,
        "vel_perseguicao": 230,
        "alcance_tiles": 7,
        "rota": [(18, 14), (42, 14), (42, 24), (18, 24)],
        "mapa": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWW.W.T..W...WWW..WWW...WW....W.WWWW.W.WWW.....WWWWAAAAAWWWW",
            "WWW........M.WWWW...........M...............K..WWWAAMAEAWWAW",
            "WWW.F...Z....WWW....E..........T....J.N.M.Q....WWWAAAAAAAAAW",
            "WWW..........WWW.T..........E.....E..............DAAAAA&AAAW",
            "WWW.....E....WWW..M.......................E....WWWAAEAAAAAWW",
            "WW....J......WWWW................W....E......M.WWWAAAAAAAAWW",
            "WW.M.........D....W.WW..WW.W....WWW.W...W.W....WWWAAAAAAAAAW",
            "WW........T..WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWAWAAAAAMAW",
            "WW...........WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWAWAAWAAAAW",
            "WW.L.E.......WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWWWWWWWWWWW",
            "WW........O..WWW...WWW.WWWWWW...WWW.....W....WWWBBBBBBBBWWWW",
            "WW......C...WWWWW.............M............O.WWWWBMBBBBBBBBW",
            "WW..WW.....WWWWWW......N...T............E....WWWBBBBBBBBFBWW",
            "WWWWWWWWWWWWWWWW....E....E......J...........WWWWBBBBEBBBBBWW",
            "WWWWWWWWWWWWWWWW..............P..............WWWBBZBBBBBBBWW",
            "WWWWWWWWWWWWWWWW.................E.Z.N...T..WWWWBBBBBBBBJBWW",
            "WWBWBBBBBBBBBWWW..M...E................Z.......DBBBBBBBBBBWW",
            "WWBBBBBBBBXBBWWW.................T...........WWWBBQBBZBBBBBW",
            "WWWBKBBBBBBBBWWW.E............C..........J.J.WWWBBBBBBBBBMBW",
            "WWBBBBBMBBBBWWWW...T................E........WWWBBBBBBBBBBBW",
            "WWBBBBBBBBBBW........Q....E......J..........WWWWBBXBBBBBBWWW",
            "WWBEBBBBBBBBB..........................E..M.WWWWWBBBBBBBBBWW",
            "WWBBBBBBBEBBBWWWW...W.W.M.....E.W....Z.......WWWBBBBBBBEBWWW",
            "WWBBBBBBBBBBBWWW....WWW....WW...WW.W...W.....WWWWBBBNBBBBWWW",
            "WWBXBBQBBBBBBWWWWWWWWWWWWWWWWW..WWWWWWWWWWWWWWWWBBBBBBCBBBBW",
            "WWBBBBBBBBBBWWWWWWWWWWWWWWWWW...WWWWWWWWWWWWWWWWBOBBBBBBBBBW",
            "WWBBBBUBQBLBBWWWWWWWWWWWAAAWAAHAAWATAWWWWWWWWWWWBBBBBBBBJBWW",
            "WWBBBBBBBBBBBWWWWWWWWWWWATAAAAAAAAAAMWWWWWWWWWWWWBBBBBBBBBBW",
            "WWBBBBBBBBBMBWWWWWWWWWWWAAEAAAAAAAKAAWWWWWWWWWWWWBBJBUBBBXBW",
            "WWBZBBBBQBEBBWWWWWWWWWWWAMAAAASAAAAAAWWWWWWWWWWWWBBBBBBBBBBW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAWAAAAAEAOAWWWWWWWWWWWBBBBMBBBBWWW",
            "WWWBBWWWBWBBBWWWWWWWWWWWAWAWWWAWAAAAAWWWWWWWWWWWBBWBBBWBWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "zona": [
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWW.W....W...WWW..WWW...WW....W.WWWW.W.WWW.....WWWWAAAAAWWWW",
            "WWW..........WWWW..............................WWWAAAAAAWWAW",
            "WWW..........WWW...............................WWWAAAAAAAAAW",
            "WWW..........WWW.................................AAAAAAAAAAW",
            "WWW..........WWW...............................WWWAAAAAAAAWW",
            "WW...........WWWW................W.............WWWAAAAAAAAWW",
            "WW................W.WW..WW.W....WWW.W...W.W....WWWAAAAAAAAAW",
            "WW...........WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWAWAAAAAAAW",
            "WW...........WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWAWAAWAAAAW",
            "WW...........WWWWWWWWW..WWWWWWWWWWWWWW..WWWWWWWWWWWWWWWWWWWW",
            "WW...........WWW...WWW.WWWWWW...WWW.....W....WWWBBBBBBBBWWWW",
            "WW..........WWWWW............................WWWWBBBBBBBBBBW",
            "WW..WW.....WWWWWW............................WWWBBBBBBBBBBWW",
            "WWWWWWWWWWWWWWWW............................WWWWBBBBBBBBBBWW",
            "WWWWWWWWWWWWWWWW.............................WWWBBBBBBBBBBWW",
            "WWWWWWWWWWWWWWWW............................WWWWBBBBBBBBBBWW",
            "WWBWBBBBBBBBBWWW................................BBBBBBBBBBWW",
            "WWBBBBBBBBBBBWWW.............................WWWBBBBBBBBBBBW",
            "WWWBBBBBBBBBBWWW.............................WWWBBBBBBBBBBBW",
            "WWBBBBBBBBBBWWWW.............................WWWBBBBBBBBBBBW",
            "WWBBBBBBBBBBW...............................WWWWBBBBBBBBBWWW",
            "WWBBBBBBBBBBB...............................WWWWWBBBBBBBBBWW",
            "WWBBBBBBBBBBBWWWW...W.W.........W............WWWBBBBBBBBBWWW",
            "WWBBBBBBBBBBBWWW....WWW....WW...WW.W...W.....WWWWBBBBBBBBWWW",
            "WWBBBBBBBBBBBWWWWWWWWWWWWWWWWW..WWWWWWWWWWWWWWWWBBBBBBBBBBBW",
            "WWBBBBBBBBBBWWWWWWWWWWWWWWWWW...WWWWWWWWWWWWWWWWBBBBBBBBBBBW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAWAAAAAWAAAWWWWWWWWWWWBBBBBBBBBBWW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAAAAAAAAAAAWWWWWWWWWWWWBBBBBBBBBBW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAAAAAAAAAAAWWWWWWWWWWWWBBBBBBBBBBW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAAAAAAAAAAAWWWWWWWWWWWWBBBBBBBBBBW",
            "WWBBBBBBBBBBBWWWWWWWWWWWAAAWAAAAAAAAAWWWWWWWWWWWBBBBBBBBBWWW",
            "WWWBBWWWBWBBBWWWWWWWWWWWAWAWWWAWAAAAAWWWWWWWWWWWBBWBBBWBWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
            "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
        ],
        "subs": [
            {
                "mapa": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWBBBWWBRBBWWWWWWBBBBWBBWBXBWW",
                    "WWBVBWWBBBWWWWWWBBNMBBBBBBBBWW",
                    "WWBBBBBBWWWWWWWWBBBBBBBBBKBWWW",
                    "WWWBBUBBBBBBBMBBBBBBCBBBBBBWWW",
                    "WWWBBBBBBBWWBBBWBBBBBBBBBBWWWW",
                    "WWBBBWWBBBBWWWWWBXBWBBBBMBWWWW",
                    "WWWBBWWBBBJWWWWWBBBWWBBBBBWWWW",
                    "WWBBWWWBWBBWWWWWWWWWWBWWWWWWWW",
                    "WWWBBWWWWWWWWWWWWWWWWBWWWWWWWW",
                    "WWWWBWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWBWWWWBBWBBWWBBBBBBBWBWWWWW",
                    "WWWWBWWBBBBBBBBBBJBBMBBBBBBWWW",
                    "WWWBBWWBBMBBBBCBBBBBBBBBBBBWWW",
                    "WWWBBBBBBBBBOBBBBBBBBBBBBFBWWW",
                    "WWBBMBBXBBBBBBBMBBBBBWBVBBBBWW",
                    "WWBBBBBBBWBWBBBBBBBRBWBBBBXBWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
                "zona": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWBBBWWBBBBWWWWWWBBBBWBBWBBBWW",
                    "WWBBBWWBBBWWWWWWBBBBBBBBBBBBWW",
                    "WWBBBBBBWWWWWWWWBBBBBBBBBBBWWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWWBBBBBBBWWBBBWBBBBBBBBBBWWWW",
                    "WWBBBWWBBBBWWWWWBBBWBBBBBBWWWW",
                    "WWWBBWWBBBBWWWWWBBBWWBBBBBWWWW",
                    "WWBBWWWBWBBWWWWWWWWWWBWWWWWWWW",
                    "WWWBBWWWWWWWWWWWWWWWWBWWWWWWWW",
                    "WWWWBWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWBWWWWBBWBBWWBBBBBBBWBWWWWW",
                    "WWWWBWWBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWWBBWWBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWBBBBBBBBBBBBBBBBBBBWBBBBBBWW",
                    "WWBBBBBBBWBWBBBBBBBBBWBBBBBBWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
            },
            {
                "mapa": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWBXBWWBBBBWWBWWWWWWWBBBBWBBBWW",
                    "WWWBBBBBBBMBBWBWWWWWWBBBNBBBBBWW",
                    "WWWBBKBBBBBVBBBWWWWWBBBGBGBBWWWW",
                    "WWWWBBBBBCBBBBBBBMBBBBBBBBUBBWWW",
                    "WWWWWBBBBBBBBBBWBBBWBBBBBBBBBWWW",
                    "WWWWWBMBBBWBBXBWWWWWWBBBBWBBBBWW",
                    "WWWBBBBBWWWBBBBWWWWWBBBBBWBBBWWW",
                    "WWWWWWWBWWWWWWWWWWWWWBRBWWWWWWWW",
                    "WWWWWWWBBWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWBBBWWBWBBWWBWWBRBWWWBBBBBBWWW",
                    "WWWBYBBBBBBBBBBBBBBBBBBBMBBVBBWW",
                    "WWWBBBBBBBBBBBMBCBBBBBBBBBBBBBWW",
                    "WWWBOBWBMBBBBBBBBBBBBJBBBBBBFBWW",
                    "WWWBBBWBBBBBXBBWBBBBMBBBBBBBBBWW",
                    "WWWWWWWWWWBBBBWWBWWBBBWBBXBWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
                "zona": [
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWBBBWWBBBBWWBWWWWWWWBBBBWBBBWW",
                    "WWWBBBBBBBBBBWBWWWWWWBBBBBBBBBWW",
                    "WWWBBBBBBBBBBBBWWWWWBBBBBBBBWWWW",
                    "WWWWBBBBBBBBBBBBBBBBBBBBBBBBBWWW",
                    "WWWWWBBBBBBBBBBWBBBWBBBBBBBBBWWW",
                    "WWWWWBBBBBWBBBBWWWWWWBBBBWBBBBWW",
                    "WWWBBBBBWWWBBBBWWWWWBBBBBWBBBWWW",
                    "WWWWWWWBWWWWWWWWWWWWWBBBWWWWWWWW",
                    "WWWWWWWBBWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWBWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWBBBWWBWBBWWBWWBBBWWWBBBBBBWWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWWBBBBBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWWBBBWBBBBBBBBBBBBBBBBBBBBBBBWW",
                    "WWWBBBWBBBBBBBBWBBBBBBBBBBBBBBWW",
                    "WWWWWWWWWWBBBBWWBWWBBBWBBBBWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
                ],
            },
        ],
    },
]

estado = "MENU"
janela_dt = 0.0
motivo_derrota = ""
nivel_atual = 0

mapa_atual = []
zona_atual = []
largura_mapa = 1
altura_mapa = 1
mundo_largura = 1
mundo_altura = 1
mapa_surf = None
subterraneo = False
camada_sub = None
camada_sup = None
alcapoes = {}
luzes = []
alcapao_usado = None
bloqueio_alcapao = False
paredes_set = set()
portas_set = set()
chaves = []
fragmentos = []
moedas = []
pocoes = []
elfos = []
renas = []
decor_din = []
moedas_coletadas = 0
fragmentos_total = 0
spawn_tile = (0, 0)
boss_tile_inicial = (0, 0)

rota_atual = []
rota_idx = 0
vel_patrulha = 110
vel_perseguicao = 170
alcance_px = 300
caminho_boss = []
timer_caminho = 0.0
boss_cx = 0.0
boss_cy = 0.0
pausa_papai = 0.0

magia_natal = MAGIA_INICIAL
inventario_chaves = 0
fragmentos_coletados = 0
tempo_protegido = 0.0
nico_x = 0.0
nico_y = 0.0

mensagem = ""
mensagem_tempo = 0.0

_sprites = {}


def sprite_arquivo(nome):
    if nome not in _sprites:
        _sprites[nome] = Sprite(nome)
    return _sprites[nome]


def hash_tile(c, r):
    return ((c * 73856093) ^ (r * 19349663)) & 0xffff


class Animacao:
    def __init__(self, arquivos, duracao_quadro):
        self.quadros = [sprite_arquivo(a) for a in arquivos]
        self.duracao = duracao_quadro
        self.tempo = 0.0
        self.indice = 0

    def avancar(self, dt):
        self.tempo += dt
        self.indice = int(self.tempo / self.duracao) % len(self.quadros)

    def atual(self):
        return self.quadros[self.indice]


BOTAO_JOGAR = Sprite("botao_jogar.png")
BOTAO_JOGAR.set_position(janela.width // 2 - BOTAO_JOGAR.width // 2, 352)

nico_andar = {d: Animacao([f"nico_walk_{d}_{i}.png" for i in range(4)], VEL_ANIM_NICO_ANDAR)
              for d in DIRECOES}
nico_parado = {d: Animacao([f"nico_idle_{d}_{i}.png" for i in range(16)], VEL_ANIM_NICO_PARADO)
               for d in DIRECOES}
NICO_W = nico_parado["down"].atual().width
NICO_H = nico_parado["down"].atual().height
nico_dir = "down"
nico_atual = nico_parado["down"].atual()

papai_andar = {
    "dir": Animacao([f"papai_dir_{i}.png" for i in range(6)], VEL_ANIM_PAPAI),
    "esq": Animacao([f"papai_esq_{i}.png" for i in range(6)], VEL_ANIM_PAPAI),
}
papai_parado = Animacao(["papai_parado.png"], 1.0)
papai_dir = "dir"
papai_atual = papai_parado.atual()

spr_porta = sprite_arquivo("porta.png")
chao_neve = [sprite_arquivo(f"chao_neve_{i}.png") for i in range(1, 5)]
chao_alto = [sprite_arquivo(f"chao_alto_{i}.png") for i in range(1, 3)]
chao_caverna = [sprite_arquivo(f"chao_caverna_{i}.png") for i in range(1, 5)]
DECOR_ESTATICO = {
    "R": ["pedra_neve.png"],
    "X": ["cristal.png", "cristal_pequeno.png"],
    "Y": [f"boneco_{i}.png" for i in range(5)],
    "V": ["monte_neve.png"],
    "G": [f"presente_{i}.png" for i in range(5)],
    "b": ["arbusto_neve.png", "arbusto_neve_2.png"],
    "J": [f"presentinho_{i}.png" for i in range(5)] + [f"meia_{i}.png" for i in range(1, 6)],
    "Q": ["bengala.png", "poste_doce.png"],
    "L": ["treno.png"],
}
DECOR_ANIMADO = {
    "T": ([f"arvore_natal_{i}.png" for i in range(9)], 0.12),
    "C": ([f"fogueira_{i}.png" for i in range(5)], 0.15),
    "N": (["arvore_enfeitada_0.png", "arvore_enfeitada_2.png", "arvore_enfeitada_1.png", "arvore_enfeitada_2.png"], 0.35),
    "H": ([f"holo_{i}.png" for i in range(8)], 0.1),
    "Z": ([f"poste_{i}.png" for i in range(4)], 0.3),
    "&": ([f"livro_{i}.png" for i in range(3)], 0.25),
}
LUZES_FRAMES = [f"luzes_{i}.png" for i in range(4)]
VEL_RENA = 45
RENAS_POR_NIVEL = 4
PORTAL_FRAMES = ["portal_off.png", "portal_mid.png", "portal_on.png", "portal_on.png", "portal_mid.png"]

neve_rng = random.Random(7)
flocos = [[neve_rng.uniform(0, 1200), neve_rng.uniform(0, 700), neve_rng.uniform(25, 70),
           neve_rng.uniform(-12, 12), neve_rng.choice([1, 2, 2, 3])] for _ in range(NEVE_QUANTIDADE)]

cam = Camera(janela.width, janela.height)


def resetar_camera():
    global cam
    cam = Camera(janela.width, janela.height)
    cam.set_world_bounds(mundo_largura, mundo_altura)


def mostrar(texto):
    global mensagem, mensagem_tempo
    mensagem = texto
    mensagem_tempo = TEMPO_MENSAGEM


def centro_tile(tile):
    return (tile[0] * TAMANHO_TILE + TAMANHO_TILE / 2, tile[1] * TAMANHO_TILE + TAMANHO_TILE / 2)


def tile_de(x, y):
    return (int(x // TAMANHO_TILE), int(y // TAMANHO_TILE))


def tile_livre(tile):
    c, r = tile
    if c < 0 or r < 0 or c >= largura_mapa or r >= altura_mapa:
        return False
    return tile not in paredes_set and tile not in portas_set


def bfs(inicio, destino):
    if inicio == destino:
        return []
    fila = deque([inicio])
    pai = {inicio: None}
    while fila:
        atual = fila.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            viz = (atual[0] + dc, atual[1] + dr)
            if viz in pai or not tile_livre(viz):
                continue
            pai[viz] = atual
            if viz == destino:
                caminho = []
                no = viz
                while no != inicio:
                    caminho.append(no)
                    no = pai[no]
                caminho.reverse()
                return caminho
            fila.append(viz)
    return []


def caixa_nico(x, y):
    return (x + (NICO_W - HITBOX_NICO[0]) / 2,
            y + (NICO_H - HITBOX_NICO[1]),
            HITBOX_NICO[0], HITBOX_NICO[1])


def bloqueado(x, y, w, h):
    c1, r1 = tile_de(x, y)
    c2, r2 = tile_de(x + w - 1, y + h - 1)
    for c in range(c1, c2 + 1):
        for r in range(r1, r2 + 1):
            if not tile_livre((c, r)):
                return True
    return False


def sobrepoe(a, b):
    return (a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and
            a[1] < b[1] + b[3] and a[1] + a[3] > b[1])


def caminho_passeio(origem):
    for _ in range(25):
        destino = (origem[0] + random.randint(-RAIO_PASSEIO_ELFO, RAIO_PASSEIO_ELFO),
                   origem[1] + random.randint(-RAIO_PASSEIO_ELFO, RAIO_PASSEIO_ELFO))
        if destino != origem and tile_livre(destino):
            caminho = bfs(origem, destino)
            if caminho:
                return caminho
    return []


class Elfo:
    def __init__(self, tile):
        self.tile = tile
        self.cx, self.cy = centro_tile(tile)
        self.caminho = []
        self.espera = random.uniform(0.3, 1.5)
        self.dir = "down"
        self.morto = False
        self.tempo_morte = 0.0
        self.andar = {d: Animacao([f"elfo_walk_{d}_{i}.png" for i in range(4)], VEL_ANIM_ELFO_ANDAR)
                      for d in DIRECOES}
        self.parado = {d: Animacao([f"elfo_idle_{d}_{i}.png" for i in range(4)], VEL_ANIM_ELFO_PARADO)
                       for d in DIRECOES}
        self.morte = Animacao([f"elfo_morte_{i}.png" for i in range(4)], VEL_ANIM_ELFO_MORTE)
        self.sprite = self.parado["down"].atual()

    def morrer(self):
        self.morto = True
        self.tempo_morte = 0.0
        self.caminho = []

    def proximo_tile_fuga(self):
        melhor = None
        melhor_d = -1
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            viz = (self.tile[0] + dc, self.tile[1] + dr)
            if not tile_livre(viz):
                continue
            vx, vy = centro_tile(viz)
            d = math.hypot(vx - boss_cx, vy - boss_cy) + random.uniform(0, 8)
            if d > melhor_d:
                melhor_d = d
                melhor = viz
        return melhor

    def atualizar(self, dt):
        if self.morto:
            self.tempo_morte += dt
            self.morte.avancar(dt)
            self.sprite = self.morte.atual()
            return
        andando = False
        com_medo = math.hypot(self.cx - boss_cx, self.cy - boss_cy) < RAIO_MEDO_ELFO
        if com_medo:
            self.espera = 0
            if not self.caminho:
                fuga = self.proximo_tile_fuga()
                self.caminho = [fuga] if fuga else []
            elif len(self.caminho) > 1:
                self.caminho = self.caminho[:1]
        if self.espera > 0:
            self.espera -= dt
        elif self.caminho:
            alvo = centro_tile(self.caminho[0])
            dx = alvo[0] - self.cx
            dy = alvo[1] - self.cy
            dist = math.hypot(dx, dy)
            passo = (VEL_ELFO_FUGA if com_medo else VEL_ELFO) * dt
            if dist <= passo:
                self.cx, self.cy = alvo
                self.tile = self.caminho.pop(0)
            else:
                self.cx += dx / dist * passo
                self.cy += dy / dist * passo
            andando = True
            if abs(dx) >= abs(dy):
                self.dir = "right" if dx > 0 else "left"
            else:
                self.dir = "down" if dy > 0 else "up"
        else:
            self.espera = random.uniform(0.8, 2.0)
            self.caminho = caminho_passeio(self.tile)
        grupo = self.andar if andando else self.parado
        grupo[self.dir].avancar(dt)
        self.sprite = grupo[self.dir].atual()

    def desenhar(self):
        self.sprite.set_position(self.cx - self.sprite.width / 2, self.cy - self.sprite.height / 2)
        self.sprite.draw()


class Rena:
    def __init__(self, tile, tipo):
        self.tile = tile
        self.cx, self.cy = centro_tile(tile)
        self.alvo = None
        self.espera = random.uniform(0.5, 3.0)
        self.dir = "down"
        self.andar = {d: Animacao([f"{tipo}_{d}_{i}.png" for i in (0, 1, 2, 1)], 0.18) for d in DIRECOES}
        self.sprite = self.andar["down"].quadros[1]

    def atualizar(self, dt):
        if self.espera > 0:
            self.espera -= dt
            self.sprite = self.andar[self.dir].quadros[1]
            return
        if self.alvo is None:
            opcoes = [(self.tile[0] + dc, self.tile[1] + dr) for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            opcoes = [t for t in opcoes if rena_pode(t)]
            if not opcoes:
                self.espera = 2.0
                return
            frente = [t for t in opcoes if t == (self.tile[0] + DELTA[self.dir][0], self.tile[1] + DELTA[self.dir][1])]
            self.alvo = frente[0] if frente and random.random() < 0.7 else random.choice(opcoes)
        ax, ay = centro_tile(self.alvo)
        dx, dy = ax - self.cx, ay - self.cy
        dist = math.hypot(dx, dy)
        if abs(dx) >= abs(dy):
            self.dir = "right" if dx > 0 else "left"
        else:
            self.dir = "down" if dy > 0 else "up"
        passo = VEL_RENA * dt
        if dist <= passo:
            self.cx, self.cy = ax, ay
            self.tile = self.alvo
            self.alvo = None
            if random.random() < 0.25:
                self.espera = random.uniform(1.0, 4.0)
        else:
            self.cx += dx / dist * passo
            self.cy += dy / dist * passo
        self.andar[self.dir].avancar(dt)
        self.sprite = self.andar[self.dir].atual()

    def desenhar(self):
        x = self.cx - self.sprite.width / 2
        y = self.cy - self.sprite.height / 2
        if x + self.sprite.width < cam.x or x > cam.x + janela.width or y + self.sprite.height < cam.y or y > cam.y + janela.height:
            return
        self.sprite.set_position(x, y)
        self.sprite.draw()


ocupado_plato = set()


def rena_pode(t):
    return interior_plato(*t) and t not in ocupado_plato and (t[0], t[1] - 1) not in ocupado_plato and (t[0], t[1] + 1) not in ocupado_plato


DELTA = {"down": (0, 1), "up": (0, -1), "left": (-1, 0), "right": (1, 0)}


def criar_renas():
    rng = random.Random(nivel_atual * 31 + 7)
    lugares = [(c, r) for r in range(1, altura_mapa - 1) for c in range(1, largura_mapa - 1) if rena_pode((c, r))]
    rng.shuffle(lugares)
    return [Rena(t, "rudolph" if i == 0 else "rena") for i, t in enumerate(lugares[:RENAS_POR_NIVEL])]


def elfos_vivos():
    return [e for e in elfos if not e.morto]


def alvo_papai():
    ncx = nico_x + NICO_W / 2
    ncy = nico_y + NICO_H / 2
    if math.hypot(ncx - boss_cx, ncy - boss_cy) < alcance_px:
        return (ncx, ncy, True)
    vivos = elfos_vivos()
    if vivos:
        mais_perto = min(vivos, key=lambda e: math.hypot(e.cx - boss_cx, e.cy - boss_cy))
        if math.hypot(mais_perto.cx - boss_cx, mais_perto.cy - boss_cy) < ALCANCE_CACA_ELFO:
            return (mais_perto.cx, mais_perto.cy, False)
    return None


CAMADA = ["mapa_atual", "zona_atual", "largura_mapa", "altura_mapa", "mundo_largura", "mundo_altura",
          "mapa_surf", "paredes_set", "portas_set", "chaves", "fragmentos", "moedas", "pocoes",
          "decor_din", "spawn_tile", "alcapoes", "luzes", "subterraneo"]


def salvar_camada():
    return {k: globals()[k] for k in CAMADA}


def restaurar_camada(dados):
    globals().update(dados)


def montar_camada(mapa, zona, sub):
    global mapa_atual, zona_atual, largura_mapa, altura_mapa, mundo_largura, mundo_altura
    global paredes_set, portas_set, chaves, fragmentos, moedas, pocoes, decor_din
    global spawn_tile, boss_tile_inicial, alcapoes, luzes, subterraneo
    subterraneo = sub
    mapa_atual = mapa
    zona_atual = zona
    altura_mapa = len(mapa_atual)
    largura_mapa = len(mapa_atual[0])
    mundo_largura = largura_mapa * TAMANHO_TILE
    mundo_altura = altura_mapa * TAMANHO_TILE
    paredes_set = set()
    portas_set = set()
    chaves = []
    fragmentos = []
    moedas = []
    pocoes = []
    decor_din = []
    alcapoes = {}
    luzes = []
    for r, linha in enumerate(mapa_atual):
        for c, ch in enumerate(linha):
            tile = (c, r)
            if ch == 'W' or ch in BLOQUEANTES:
                paredes_set.add(tile)
            if ch == 'D':
                portas_set.add(tile)
            elif ch == 'U':
                alcapoes[tile] = sub
                if sub:
                    spawn_tile = tile
                    luzes.append((centro_tile(tile), "media"))
            elif ch == 'K':
                k = Sprite("chave.png")
                k.set_position(c * TAMANHO_TILE + 16, r * TAMANHO_TILE + 16)
                chaves.append(k)
            elif ch == 'F':
                f = Sprite("fragmento.png")
                f.set_position(c * TAMANHO_TILE + 16, r * TAMANHO_TILE + 16)
                fragmentos.append(f)
            elif ch == 'M':
                m = Sprite("moeda.png")
                m.set_position(c * TAMANHO_TILE + 16, r * TAMANHO_TILE + 16)
                moedas.append(m)
            elif ch == 'O':
                p = Sprite("pocao.png")
                p.set_position(c * TAMANHO_TILE + 16, r * TAMANHO_TILE + 14)
                pocoes.append(p)
            elif ch == 'E' and not sub:
                elfos.append(Elfo(tile))
            elif ch in DECOR_ANIMADO:
                arquivos, duracao = DECOR_ANIMADO[ch]
                decor_din.append(criar_decor(c, r, arquivos, duracao))
                if ch == 'C':
                    luzes.append((centro_tile(tile), "grande"))
                elif ch in "NTHZ&" and (sub or tema_atual == "noite"):
                    luzes.append(((c * TAMANHO_TILE + 32, r * TAMANHO_TILE), "media"))
            elif ch == 'X' and sub:
                luzes.append((centro_tile(tile), "pequena"))
            elif ch == 'S':
                spawn_tile = tile
            elif ch == 'P':
                boss_tile_inicial = tile
    construir_mapa_surf()


EQUACOES = {
    3: [("X + 5 = 7", (2,)), ("X - 3 = 4", (7,)), ("2X = 10", (5,)), ("X + 8 = 15", (7,)),
        ("3X = 12", (4,)), ("X - 6 = 3", (9,)), ("2X + 1 = 9", (4,))],
    4: [("X² - 6 = 10", (4, -4)), ("X² + 6 = 31", (5, -5)), ("X² = 49", (7, -7)), ("X² - 9 = 0", (3, -3)),
        ("2X² = 50", (5, -5)), ("X² + X = 12", (3, -4)), ("X² - 1 = 63", (8, -8))],
}
camadas_sub = []
sub_atual = 0
alcapao_sub = {}
tema_atual = "dia"
livro_tile = None
equacao = None
equacao_aberta = False
resposta = ""
erro_tempo = 0.0


def carregar_nivel(indice):
    global nivel_atual, fragmentos_total, rota_atual, rota_idx, vel_patrulha, vel_perseguicao
    global alcance_px, caminho_boss, timer_caminho, boss_cx, boss_cy
    global magia_natal, inventario_chaves, fragmentos_coletados, tempo_protegido
    global nico_x, nico_y, nico_atual, nico_dir, mensagem, mensagem_tempo
    global moedas_coletadas, elfos, papai_dir, papai_atual, pausa_papai, renas
    global camadas_sub, camada_sup, alcapao_usado, bloqueio_alcapao, alcapao_sub, sub_atual
    global tema_atual, livro_tile, equacao, equacao_aberta, resposta, erro_tempo

    nivel = NIVEIS[indice]
    nivel_atual = indice
    tema_atual = nivel["tema"]
    elfos = []
    moedas_coletadas = 0
    camadas_sub = []
    camada_sup = None
    sub_atual = 0
    brilhos.clear()
    popups.clear()
    alcapao_usado = None
    bloqueio_alcapao = False
    equacao_aberta = False
    resposta = ""
    erro_tempo = 0.0
    frag_sub = 0
    for sub in nivel["subs"]:
        montar_camada(sub["mapa"], sub["zona"], True)
        camadas_sub.append(salvar_camada())
        frag_sub += len(fragmentos)
    montar_camada(nivel["mapa"], nivel["zona"], False)
    alcapao_sub = {t: i for i, t in enumerate(alcapoes)}
    livro_tile = next(((c, r) for r, linha in enumerate(mapa_atual) for c, ch in enumerate(linha) if ch == '&'), None)
    equacao = random.choice(EQUACOES[indice]) if livro_tile and indice in EQUACOES else None
    renas = criar_renas()
    fragmentos_total = len(fragmentos) + frag_sub
    vel_patrulha = nivel["vel_patrulha"]
    vel_perseguicao = nivel["vel_perseguicao"]
    alcance_px = nivel["alcance_tiles"] * TAMANHO_TILE
    rota_atual = nivel["rota"]
    rota_idx = 0
    caminho_boss = []
    timer_caminho = 0.0

    cx, cy = centro_tile(spawn_tile)
    nico_dir = "down"
    nico_atual = nico_parado["down"].atual()
    nico_x = cx - NICO_W / 2
    nico_y = cy - NICO_H / 2
    nico_atual.set_position(nico_x, nico_y)
    boss_cx, boss_cy = centro_tile(boss_tile_inicial)
    papai_dir = "dir"
    papai_atual = papai_parado.atual()
    pausa_papai = 0.0

    magia_natal = MAGIA_INICIAL
    inventario_chaves = 0
    fragmentos_coletados = 0
    tempo_protegido = 0.0


def posicionar_nico(tile):
    global nico_x, nico_y
    cx, cy = centro_tile(tile)
    nico_x = cx - NICO_W / 2
    nico_y = cy - NICO_H / 2
    nico_atual.set_position(nico_x, nico_y)


def entrar_subterraneo(tile):
    global camada_sup, alcapao_usado, bloqueio_alcapao, sub_atual
    camada_sup = salvar_camada()
    alcapao_usado = tile
    sub_atual = alcapao_sub[tile]
    restaurar_camada(camadas_sub[sub_atual])
    brilhos.clear()
    popups.clear()
    posicionar_nico(spawn_tile)
    bloqueio_alcapao = True
    resetar_camera()
    cam.follow(nico_atual, suavizacao=1.0)
    mostrar("Você desceu para o subterrâneo!")


def sair_subterraneo():
    global bloqueio_alcapao
    camadas_sub[sub_atual] = salvar_camada()
    restaurar_camada(camada_sup)
    brilhos.clear()
    popups.clear()
    posicionar_nico(alcapao_usado)
    bloqueio_alcapao = True
    resetar_camera()
    cam.follow(nico_atual, suavizacao=1.0)
    mostrar("De volta à superfície!")


def perto_do_livro():
    if livro_tile is None or subterraneo:
        return False
    lx, ly = centro_tile(livro_tile)
    return math.hypot(nico_x + NICO_W / 2 - lx, nico_y + NICO_H / 2 - ly) < 110


def desenhar_equacao():
    tela = Window.get_screen()
    painel = sprite_arquivo("painel_equacao.png").image
    px = janela.width // 2 - painel.get_width() // 2
    py = janela.height - painel.get_height() - 12
    tela.blit(painel, (px, py))
    cab = renderizar("O LIVRO PERGUNTA: QUANTO VALE X?", 2, (120, 60, 40), (250, 240, 220))
    tela.blit(cab, (janela.width // 2 - cab.get_width() // 2, py + 26))
    eq = renderizar(equacao[0], 5, (200, 40, 50), (60, 10, 18))
    tela.blit(eq, (janela.width // 2 - eq.get_width() // 2, py + 58))
    caixa = pygame.Rect(janela.width // 2 - 110, py + 128, 220, 56)
    tela.fill((60, 40, 36), caixa.inflate(8, 8))
    tela.fill((250, 246, 230), caixa)
    cursor = "_" if int(tempo_luz * 2) % 2 == 0 else " "
    txt = renderizar("X = " + resposta + cursor, 4, (40, 30, 30), None)
    tela.blit(txt, (caixa.x + 14, caixa.y + caixa.height // 2 - txt.get_height() // 2))
    if erro_tempo > 0:
        dica = renderizar("ERRADO! -10 DE MAGIA", 2, (230, 50, 50), (250, 240, 220))
    else:
        dica = renderizar("DIGITE O NUMERO E APERTE ENTER   ESC: SAIR", 2, (120, 90, 70), (250, 240, 220))
    tela.blit(dica, (janela.width // 2 - dica.get_width() // 2, py + 196))


def desenhar_aviso_livro():
    if livro_tile is None or subterraneo or equacao_aberta or not perto_do_livro():
        return
    tela = Window.get_screen()
    lx, ly = centro_tile(livro_tile)
    texto_livro = "E: LER O LIVRO" if fragmentos_coletados >= fragmentos_total else "FALTAM FRAGMENTOS"
    sup = renderizar(texto_livro, 2, (255, 236, 160))
    bob = math.sin(tempo_luz * 4) * 4
    tela.blit(sup, (lx - cam.x - sup.get_width() // 2, ly - cam.y - 110 + bob))


DIGITOS_NUMPAD = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
                  pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]


def ler_digitacao():
    global resposta
    for d in range(10):
        if apertou(str(d), DIGITOS_NUMPAD[d]) and len(resposta) < 4:
            resposta += str(d)
    if apertou("MINUS", pygame.K_KP_MINUS) and resposta == "":
        resposta = "-"
    if apertou("BACKSPACE"):
        resposta = resposta[:-1]


def criar_decor(c, r, arquivos, duracao):
    anim = Animacao(arquivos, duracao)
    spr = anim.atual()
    x = c * TAMANHO_TILE + (TAMANHO_TILE - spr.width) // 2
    y = r * TAMANHO_TILE + TAMANHO_TILE - spr.height
    return [anim, x, y, spr.width, spr.height]


def eh_parede(c, r):
    if c < 0 or r < 0 or c >= largura_mapa or r >= altura_mapa:
        return True
    return zona_atual[r][c] == 'W'


def perto_de_caverna(c, r):
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            cc, rr = c + dc, r + dr
            if 0 <= cc < largura_mapa and 0 <= rr < altura_mapa and zona_atual[rr][cc] == 'B':
                return True
    return False


def eh_face(c, r):
    return eh_parede(c, r) and not eh_parede(c, r + 1)


def quartos_penhasco(c, r):
    o = not eh_parede(c - 1, r)
    l = not eh_parede(c + 1, r)
    n = not eh_parede(c, r - 1)
    if not eh_parede(c, r + 1):
        return ["face_ae" if o else "face_a1", "face_ad" if l else "face_a2",
                "face_be" if o else "face_b1", "face_bd" if l else "face_b2"]

    def canto(nome, dc, dr, senao):
        return nome if not eh_parede(c + dc, r + dr) else senao

    te = "topo_ce" if n and o else "topo_n1" if n else "topo_o" if o else canto("topo_ie_ne", -1, -1, "topo_int")
    td = "topo_cd" if n and l else "topo_n2" if n else "topo_l" if l else canto("topo_ie_nd", 1, -1, "topo_int2")
    be = "topo_o" if o else canto("topo_ie_se", -1, 1, "topo_int")
    bd = "topo_l" if l else canto("topo_ie_sd", 1, 1, "topo_int2")
    return [te, td, be, bd]


def interior_plato(c, r):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not eh_parede(c + dc, r + dr):
                return False
    return True


def bloco_livre(c0, r0, c1, r1, ocupado):
    for r in range(r0, r1 + 1):
        for c in range(c0, c1 + 1):
            if (c, r) in ocupado or not interior_plato(c, r):
                return False
    return True


def decorar_platos(ocupado):
    itens = []
    for r in range(altura_mapa):
        for c in range(largura_mapa):
            if (c, r) in ocupado or not interior_plato(c, r):
                continue
            h = random.Random(c * 7919 + r * 104729).randrange(100)
            nome = None
            pinheiro_cabe = bloco_livre(c, r - 1, c, r, ocupado)
            if h < 2 and bloco_livre(c - 1, r - 2, c + 1, r, ocupado):
                nome = "casa.png"
                usados = [(cc, rr) for cc in range(c - 1, c + 2) for rr in range(r - 2, r + 1)]
            elif 2 <= h < 4 and bloco_livre(c - 1, r - 1, c + 1, r, ocupado):
                nome = f"casa_vila_{h % 2}.png"
                usados = [(cc, rr) for cc in range(c - 1, c + 2) for rr in range(r - 1, r + 1)]
            elif 4 <= h < 6 and bloco_livre(c - 1, r - 1, c + 1, r, ocupado):
                nome = "arvore_enfeitada_0.png"
                usados = [(cc, rr) for cc in range(c - 1, c + 2) for rr in range(r - 1, r + 1)]
            elif 6 <= h < 16 and pinheiro_cabe:
                nome = "pinheiro_grande.png"
                usados = [(c, r), (c, r - 1)]
            elif 16 <= h < 62 and pinheiro_cabe:
                nome = "pinheiro.png"
                usados = [(c, r), (c, r - 1)]
            elif h == 62:
                nome = f"boneco_{c % 5}.png"
                usados = [(c, r)]
            elif h == 63:
                nome = "treno.png"
                usados = [(c, r)]
            if nome:
                ocupado.update(usados)
                spr = sprite_arquivo(nome)
                x = c * TAMANHO_TILE + (TAMANHO_TILE - spr.width) // 2
                y = r * TAMANHO_TILE + TAMANHO_TILE - spr.height
                itens.append((y + spr.height, x, y, spr))
    return itens


def construir_mapa_surf():
    global mapa_surf, ocupado_plato
    mapa_surf = pygame.Surface((mundo_largura, mundo_altura))
    meio = TAMANHO_TILE // 2
    for r in range(altura_mapa):
        for c in range(largura_mapa):
            x = c * TAMANHO_TILE
            y = r * TAMANHO_TILE
            zona = zona_atual[r][c]
            if zona == 'W':
                pal = "c" if subterraneo else "p" if perto_de_caverna(c, r) else "t"
                for k, nome in enumerate(quartos_penhasco(c, r)):
                    mapa_surf.blit(sprite_arquivo(f"pen_{pal}_{nome}.png").image,
                                   (x + (k % 2) * meio, y + (k // 2) * meio))
                continue
            if subterraneo:
                fundo = sprite_arquivo(f"chao_sub_{hash_tile(c, r) % 4 + 1}.png")
                pref = "sombra_c_"
            elif zona == 'A':
                fundo = chao_alto[(c + r) % len(chao_alto)]
                pref = "sombra_"
            elif zona == 'B':
                fundo = chao_caverna[hash_tile(c, r) % len(chao_caverna)]
                pref = "sombra_p_"
            else:
                fundo = chao_neve[hash_tile(c, r) % len(chao_neve)]
                pref = "sombra_"
            mapa_surf.blit(fundo.image, (x, y))
            if subterraneo and hash_tile(c * 3, r * 5) % 4 == 0:
                mapa_surf.blit(sprite_arquivo(f"neve_chao_{hash_tile(c, r) % 4 + 1}.png").image, (x, y))
            if eh_parede(c, r - 1):
                mapa_surf.blit(sprite_arquivo(pref + "n1.png").image, (x, y))
                mapa_surf.blit(sprite_arquivo(pref + "n2.png").image, (x + meio, y))
            if eh_parede(c + 1, r):
                mapa_surf.blit(sprite_arquivo(pref + "l.png").image, (x + meio, y))
                mapa_surf.blit(sprite_arquivo(pref + "l.png").image, (x + meio, y + meio))
            if eh_parede(c - 1, r):
                mapa_surf.blit(sprite_arquivo(pref + "o.png").image, (x, y))
                mapa_surf.blit(sprite_arquivo(pref + "o.png").image, (x, y + meio))

    for r in range(altura_mapa):
        for c in range(largura_mapa):
            if not (eh_face(c, r) and eh_face(c - 1, r) and eh_face(c + 1, r)):
                continue
            h = hash_tile(c * 7, r * 3) % 17
            x = c * TAMANHO_TILE
            y = r * TAMANHO_TILE
            pedra = perto_de_caverna(c, r) and not subterraneo
            if h in ((0, 8) if subterraneo else (0,)) and not pedra:
                spr = sprite_arquivo("guirlanda.png")
                mapa_surf.blit(spr.image, (x + (TAMANHO_TILE - spr.width) // 2, y + 8))
            elif h in (4, 5, 6, 14, 15) and not pedra:
                anim = Animacao(LUZES_FRAMES, 0.3)
                anim.tempo = c * 0.3
                decor_din.append([anim, x, y - 6, TAMANHO_TILE, TAMANHO_TILE])
                if subterraneo or tema_atual == "noite":
                    luzes.append(((x + 32, y + 10), "pequena"))
            elif h == 9 or (h in (3, 12) and (pedra or subterraneo)):
                anim = Animacao(PORTAL_FRAMES, 0.25)
                anim.tempo = (c + r) * 0.17
                spr = anim.atual()
                decor_din.append([anim, x + (TAMANHO_TILE - spr.width) // 2, y, spr.width, spr.height])
                if subterraneo or tema_atual == "noite":
                    luzes.append(((x + 32, y + 32), "pequena"))

    ocupado_plato = set()
    itens = [] if subterraneo else decorar_platos(ocupado_plato)
    for r, linha in enumerate(mapa_atual):
        for c, ch in enumerate(linha):
            if ch in DECOR_ESTATICO:
                opcoes = DECOR_ESTATICO[ch]
                spr = sprite_arquivo(opcoes[hash_tile(c, r) % len(opcoes)])
                x = c * TAMANHO_TILE + (TAMANHO_TILE - spr.width) // 2
                y = r * TAMANHO_TILE + TAMANHO_TILE - spr.height - 4
                itens.append((y + spr.height, x, y, spr))
    for _, x, y, spr in sorted(itens, key=lambda t: t[0]):
        mapa_surf.blit(spr.image, (x, y))


def iniciar_nivel(indice):
    tocar("sfx_clique")
    carregar_nivel(indice)
    resetar_camera()
    cam.follow(nico_atual, suavizacao=1.0)
    mostrar(f"Nível {indice + 1}: {NIVEIS[indice]['nome']}")


def mover_papai(dt):
    global caminho_boss, timer_caminho, rota_idx, boss_cx, boss_cy, pausa_papai
    if pausa_papai > 0:
        pausa_papai -= dt
        return
    perseguindo = alvo_papai()
    if perseguindo is not None:
        timer_caminho -= dt
        if timer_caminho <= 0 or not caminho_boss:
            caminho_boss = bfs(tile_de(boss_cx, boss_cy), tile_de(perseguindo[0], perseguindo[1]))
            timer_caminho = ALCANCE_ESPERA_PAPAI
        velocidade = vel_perseguicao if perseguindo[2] else vel_perseguicao * FATOR_CACA_ELFO
    else:
        velocidade = vel_patrulha
        if not caminho_boss and rota_atual:
            n = len(rota_atual)
            for _ in range(n):
                destino = rota_atual[rota_idx]
                if tile_de(boss_cx, boss_cy) == destino:
                    rota_idx = (rota_idx + 1) % n
                    continue
                caminho_boss = bfs(tile_de(boss_cx, boss_cy), destino)
                if caminho_boss:
                    break
                rota_idx = (rota_idx + 1) % n

    if caminho_boss:
        alvo = centro_tile(caminho_boss[0])
    elif perseguindo is not None:
        alvo = perseguindo[:2]
    else:
        return

    dx = alvo[0] - boss_cx
    dy = alvo[1] - boss_cy
    dist = math.hypot(dx, dy)
    passo = velocidade * dt
    if dist <= passo:
        boss_cx, boss_cy = alvo
        if caminho_boss and centro_tile(caminho_boss[0]) == alvo:
            caminho_boss.pop(0)
    else:
        boss_cx += dx / dist * passo
        boss_cy += dy / dist * passo


def desenhar_mundo():
    tela = Window.get_screen()
    tela.blit(mapa_surf, (-int(cam.x), -int(cam.y)))
    for item in decor_din:
        anim, x, y, w, h = item
        if x + w < cam.x or x > cam.x + janela.width or y + h < cam.y or y > cam.y + janela.height:
            continue
        anim.avancar(janela_dt)
        spr = anim.atual()
        spr.set_position(x, y)
        spr.draw()
    x0 = max(0, int(cam.x // TAMANHO_TILE) - 1)
    x1 = min(largura_mapa - 1, int((cam.x + janela.width) // TAMANHO_TILE) + 1)
    y0 = max(0, int(cam.y // TAMANHO_TILE) - 1)
    y1 = min(altura_mapa - 1, int((cam.y + janela.height) // TAMANHO_TILE) + 1)
    for (c, r), aberto in alcapoes.items():
        nome = "escada.png" if subterraneo else "alcapao_aberto.png" if aberto else "alcapao_fechado.png"
        spr = sprite_arquivo(nome)
        spr.set_position(c * TAMANHO_TILE, r * TAMANHO_TILE)
        spr.draw()
    for c, r in portas_set:
        if x0 <= c <= x1 and y0 <= r <= y1:
            spr_porta.set_position(c * TAMANHO_TILE, r * TAMANHO_TILE)
            spr_porta.draw()


def atualizar_neve(dt):
    for f in flocos:
        f[1] += f[2] * dt
        f[0] += f[3] * dt
        if f[1] > janela.height + 4:
            f[1] = -4
            f[0] = random.uniform(0, janela.width)
        if f[0] < -4 or f[0] > janela.width + 4:
            f[0] = random.uniform(0, janela.width)


def desenhar_neve():
    tela = Window.get_screen()
    for x, y, v, dx, r in flocos:
        pygame.draw.circle(tela, (255, 255, 255), (int(x), int(y)), r)


def texto(msg, x, y, escala=3, cor=(255, 255, 255)):
    Window.get_screen().blit(renderizar(msg, escala, cor), (x, y))


def texto_centro(msg, cy, escala=3, cor=(255, 255, 255)):
    superficie = renderizar(msg, escala, cor)
    Window.get_screen().blit(superficie, (janela.width // 2 - superficie.get_width() // 2, cy))


def tela_final(titulo, cor_titulo, subtitulo):
    desenhar_fundo_menu(janela.delta_time())
    tela = Window.get_screen()
    painel = sprite_arquivo("hud_final.png").image
    px = janela.width // 2 - painel.get_width() // 2
    py = janela.height // 2 - painel.get_height() // 2
    tela.blit(painel, (px, py))
    escala = 5 if largura_texto(titulo, 5) < painel.get_width() - 60 else 4
    texto_centro(titulo, py + 60, escala, cor_titulo)
    texto_centro(subtitulo, py + 150, 3, (255, 240, 200))


def desenhar_hud():
    tela = Window.get_screen()
    hx, hy = 12, 12
    tela.blit(sprite_arquivo("hud_painel.png").image, (hx, hy))
    tela.blit(sprite_arquivo("icone_estrela.png").image, (hx + 22, hy + 26))
    vazia = sprite_arquivo("barra_vazia.png").image
    cheia = sprite_arquivo("barra_cheia.png").image
    bx, by = hx + 68, hy + 20
    tela.blit(vazia, (bx, by))
    fracao = max(0.0, min(1.0, magia_natal / MAGIA_INICIAL))
    largura_cheia = int(9 + (cheia.get_width() - 18) * fracao)
    if fracao > 0:
        tela.blit(cheia, (bx, by), (0, 0, largura_cheia, cheia.get_height()))
    slot = sprite_arquivo("hud_slot.png").image
    for i in range(fragmentos_total):
        sx = hx + 22 + i * 54
        sy = hy + 76
        tela.blit(slot, (sx, sy))
        icone = "fragmento.png" if i < fragmentos_coletados else "icone_frag_vazio.png"
        tela.blit(sprite_arquivo(icone).image, (sx + 8, sy + 8))
    elfo = sprite_arquivo("icone_elfo.png").image
    tela.blit(elfo, (hx + 250, hy + 78))
    texto(str(len(elfos_vivos())), hx + 304, hy + 86, 3)
    tela.blit(sprite_arquivo("icone_chave.png").image, (hx + 22, hy + 146))
    texto("x" + str(inventario_chaves), hx + 74, hy + 138, 3, (255, 230, 120))
    tela.blit(sprite_arquivo("moeda.png").image, (hx + 168, hy + 136))
    texto(str(moedas_coletadas), hx + 204, hy + 138, 3, (255, 215, 90))

    nivel_painel = sprite_arquivo("hud_nivel.png").image
    nx = janela.width - nivel_painel.get_width() - 12
    tela.blit(nivel_painel, (nx, 12))
    rotulo = "SUBSOLO" if subterraneo else "NIVEL"
    sup = renderizar(rotulo, 2, (255, 240, 200))
    tela.blit(sup, (nx + nivel_painel.get_width() // 2 - sup.get_width() // 2, 30))
    num = renderizar(f"{nivel_atual + 1}/{len(NIVEIS)}", 3)
    tela.blit(num, (nx + nivel_painel.get_width() // 2 - num.get_width() // 2, 54))

    if mensagem_tempo > 0:
        desenhar_aviso(janela.height - 112)


def desenhar_aviso(y):
    tela = Window.get_screen()
    faixa = sprite_arquivo("faixa_aviso.png").image
    tela.blit(faixa, (janela.width // 2 - faixa.get_width() // 2, y))
    escala = 3 if largura_texto(mensagem, 3) < faixa.get_width() - 230 else 2
    sup = renderizar(mensagem, escala, (255, 240, 200), (60, 10, 18))
    tela.blit(sup, (janela.width // 2 - sup.get_width() // 2, y + 50 - sup.get_height() // 2))


def criar_luz(raio):
    superficie = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
    superficie.fill((255, 255, 255, 255))
    for r in range(raio, 0, -3):
        alfa = int(ESCURIDAO_ALFA * (r / raio) ** 1.4)
        pygame.draw.circle(superficie, (255, 255, 255, alfa), (raio, raio), r)
    return superficie


def criar_brilho_quente(raio):
    superficie = pygame.Surface((raio * 2, raio * 2))
    superficie.fill((0, 0, 0))
    for r in range(raio, 0, -3):
        f = 1 - r / raio
        pygame.draw.circle(superficie, (int(70 * f), int(40 * f), int(12 * f)), (raio, raio), r)
    return superficie


LUZ_NICO = [criar_luz(r) for r in (220, 228, 236, 228)]
LUZES = {"grande": criar_luz(170), "media": criar_luz(120), "pequena": criar_luz(70), "item": criar_luz(48)}
BRILHOS_QUENTES = {"grande": criar_brilho_quente(150), "media": criar_brilho_quente(100), "pequena": criar_brilho_quente(56)}
escuridao = pygame.Surface((janela.width, janela.height), pygame.SRCALPHA)
tempo_luz = 0.0


def aplicar_por_do_sol():
    tela = Window.get_screen()
    tela.fill((255, 176, 146), special_flags=pygame.BLEND_MULT)
    tela.blit(POR_DO_SOL, (0, 0))


def criar_por_do_sol():
    s = pygame.Surface((janela.width, janela.height), pygame.SRCALPHA)
    for y in range(0, janela.height, 4):
        t = y / janela.height
        cor = (int(120 + 135 * t), int(40 + 70 * t), int(110 - 70 * t), int(70 - 30 * t))
        s.fill(cor, (0, y, janela.width, 4))
    return s


POR_DO_SOL = criar_por_do_sol()


def desenhar_escuridao(dt, alfa=ESCURIDAO_ALFA, cor=(0, 0, 0)):
    escuridao.fill(cor + (alfa,))
    luz = LUZ_NICO[int(tempo_luz * 6) % len(LUZ_NICO)]
    sx = nico_x + NICO_W / 2 - cam.x
    sy = nico_y + NICO_H / 2 - cam.y
    escuridao.blit(luz, (sx - luz.get_width() // 2, sy - luz.get_height() // 2), special_flags=pygame.BLEND_RGBA_MIN)
    for item in chaves + moedas + pocoes + fragmentos:
        stamp = LUZES["item"]
        escuridao.blit(stamp, (item.x + 16 - cam.x - stamp.get_width() // 2, item.y + 16 - cam.y - stamp.get_height() // 2),
                       special_flags=pygame.BLEND_RGBA_MIN)
    for (lx, ly), tipo in luzes:
        stamp = LUZES[tipo]
        x = lx - cam.x - stamp.get_width() // 2
        y = ly - cam.y - stamp.get_height() // 2
        if x > janela.width or y > janela.height or x + stamp.get_width() < 0 or y + stamp.get_height() < 0:
            continue
        escuridao.blit(stamp, (x, y), special_flags=pygame.BLEND_RGBA_MIN)
    tela = Window.get_screen()
    tela.blit(escuridao, (0, 0))
    for (lx, ly), tipo in luzes:
        quente = BRILHOS_QUENTES[tipo]
        x = lx - cam.x - quente.get_width() // 2
        y = ly - cam.y - quente.get_height() // 2
        if x > janela.width or y > janela.height or x + quente.get_width() < 0 or y + quente.get_height() < 0:
            continue
        tela.blit(quente, (x, y), special_flags=pygame.BLEND_ADD)


GIRO_QUADROS = 16
_giros = {}
brilhos = []
sombra_item = pygame.Surface((28, 9), pygame.SRCALPHA)
pygame.draw.ellipse(sombra_item, (20, 30, 50, 70), (0, 0, 28, 9))


def criar_brilho(raio):
    t = 3
    lado = (raio * 2 + 1) * t
    s = pygame.Surface((lado, lado), pygame.SRCALPHA)
    meio = raio * t
    for k in range(-raio, raio + 1):
        cor = (255, 255, 255, 255) if k == 0 else (255, 244, 170, 230)
        s.fill(cor, (meio + k * t, meio, t, t))
        s.fill(cor, (meio, meio + k * t, t, t))
    return s


BRILHO_QUADROS = [criar_brilho(r) for r in (0, 1, 2, 1, 0)]


def quadros_giro(nome):
    if nome not in _giros:
        base = sprite_arquivo(nome).image
        w, h = base.get_size()
        lista = []
        for k in range(GIRO_QUADROS):
            c = math.cos(2 * math.pi * k / GIRO_QUADROS)
            img = pygame.transform.scale(base, (max(2, int(w * abs(c))), h))
            if c < 0:
                img = img.copy()
                img.fill((180, 180, 205, 255), special_flags=pygame.BLEND_RGBA_MULT)
            lista.append(img)
        _giros[nome] = lista
    return _giros[nome]


def desenhar_coletavel(spr, nome):
    cx = spr.x + 16 - cam.x
    base_y = spr.y + 34 - cam.y
    if cx < -40 or cx > janela.width + 40 or base_y < -40 or base_y > janela.height + 60:
        return
    tela = Window.get_screen()
    fase = spr.x * 0.013 + spr.y * 0.007
    quadros = quadros_giro(nome)
    img = quadros[int((tempo_luz * 1.3 + fase) * GIRO_QUADROS) % GIRO_QUADROS]
    bob = math.sin(tempo_luz * 3 + fase * 5) * 3
    tela.blit(sombra_item, (cx - 14, base_y - 4))
    tela.blit(img, (cx - img.get_width() / 2, base_y - img.get_height() - 8 + bob))
    if random.random() < 1.1 * janela_dt:
        brilhos.append([spr.x + 16 + random.uniform(-18, 18), spr.y + random.uniform(-8, 22), 0.0])


_rng_menu = random.Random(5)
MENU_ESTRELAS = []
while len(MENU_ESTRELAS) < 70:
    sx, sy = _rng_menu.randint(0, 1196), _rng_menu.randint(0, 360)
    if math.hypot(sx - 1048, sy - 96) > 80:
        MENU_ESTRELAS.append((sx, sy, _rng_menu.uniform(0, 6.28), _rng_menu.uniform(1.5, 4.0)))
MENU_AURORA = [f"menu_aurora_{k}.png" for k in range(12)]
menu_arvore = Animacao(["arvore_enfeitada_0.png", "arvore_enfeitada_2.png", "arvore_enfeitada_1.png", "arvore_enfeitada_2.png"], 0.35)
menu_postes = [Animacao([f"poste_{i}.png" for i in range(4)], 0.3) for _ in range(2)]
menu_elfos = [Animacao([f"elfo_walk_right_{i}.png" for i in range(4)], 0.09) for _ in range(4)]
menu_papai = Animacao([f"papai_dir_{i}.png" for i in range(6)], 0.08)
menu_renas = [Animacao([f"{tipo}_left_{i}.png" for i in (0, 1, 2, 1)], 0.2) for tipo in ("rudolph", "rena")]
menu_t = 0.0
menu_desfile = -300.0
menu_rena_x = [1250.0, 1420.0]


def desenhar_titulo_menu():
    tela = Window.get_screen()
    bob = math.sin(menu_t * 1.6) * 5
    titulo = sprite_arquivo("menu_titulo.png").image
    tela.blit(titulo, (janela.width // 2 - titulo.get_width() // 2, 22 + bob))
    sub = sprite_arquivo("menu_subtitulo.png").image
    tela.blit(sub, (janela.width // 2 - sub.get_width() // 2, 22 + titulo.get_height() - 12 + bob * 0.6))
    em_cima = mouse.is_over_object(BOTAO_JOGAR)
    botao = sprite_arquivo("botao_jogar_hover.png" if em_cima else "botao_jogar.png").image
    pulso = 0 if em_cima else int(abs(math.sin(menu_t * 2.5)) * 3)
    tela.blit(botao, (BOTAO_JOGAR.x, BOTAO_JOGAR.y - pulso))
    if em_cima:
        seta = sprite_arquivo("seta_mapa.png").image
        vai = int(abs(math.sin(menu_t * 6)) * 8)
        dir_ = pygame.transform.rotate(seta, 90)
        esq = pygame.transform.rotate(seta, -90)
        meio_y = BOTAO_JOGAR.y + botao.get_height() // 2
        tela.blit(esq, (BOTAO_JOGAR.x - esq.get_width() - 12 - vai, meio_y - esq.get_height() // 2))
        tela.blit(dir_, (BOTAO_JOGAR.x + botao.get_width() + 12 + vai, meio_y - dir_.get_height() // 2))


def desenhar_fundo_menu(dt):
    global menu_t, menu_desfile
    menu_t += dt
    tela = Window.get_screen()
    tela.blit(sprite_arquivo("menu_ceu.png").image, (0, 0))
    for sx, sy, fase, vel in MENU_ESTRELAS:
        brilho = 0.5 + 0.5 * math.sin(menu_t * vel + fase)
        if brilho < 0.15:
            continue
        tom = int(150 + 105 * brilho)
        tela.fill((tom, tom, 255), (sx, sy, 4, 4))
        if brilho > 0.8:
            tela.fill((tom, tom, 255), (sx - 4, sy, 12, 4))
            tela.fill((tom, tom, 255), (sx, sy - 4, 4, 12))
    tela.blit(sprite_arquivo(MENU_AURORA[int(menu_t * 5) % len(MENU_AURORA)]).image, (0, 20))
    tela.blit(sprite_arquivo("menu_fundo.png").image, (0, 0))
    tela.blit(sprite_arquivo("menu_chao.png").image, (0, 0))

    for i, rena in enumerate(menu_renas):
        menu_rena_x[i] -= 28 * dt
        if menu_rena_x[i] < -120:
            menu_rena_x[i] = 1300 + i * 170
        rena.avancar(dt)
        img = rena.atual().image
        tela.blit(img, (menu_rena_x[i], 600 - img.get_height() + i * 8))
    tela.blit(sprite_arquivo("menu_pinheiros.png").image, (0, 0))

    for anim, x in zip(menu_postes, (660, 960)):
        anim.avancar(dt)
        img = anim.atual().image
        tela.blit(img, (x - img.get_width() // 2, 628 - img.get_height()))
    menu_arvore.avancar(dt)
    arvore = menu_arvore.atual().image
    tela.blit(arvore, (810 - arvore.get_width() // 2, 626 - arvore.get_height()))

    menu_desfile += 150 * dt
    if menu_desfile > 1700:
        menu_desfile = -260.0
    for i, elfo in enumerate(menu_elfos):
        elfo.avancar(dt)
        img = elfo.atual().image
        x = menu_desfile + i * 80
        pulo = abs(math.sin(menu_t * 12 + i)) * 6
        tela.blit(img, (x - 320, 648 - img.get_height() - pulo))
    menu_papai.avancar(dt)
    img = menu_papai.atual().image
    tela.blit(img, (menu_desfile - 560, 652 - img.get_height()))

    atualizar_neve(dt)
    desenhar_neve()


popups = []


def popup(x, y, icone, texto, cor):
    icone_img = sprite_arquivo(icone).image
    txt = renderizar(texto, 3, cor, (40, 20, 30))
    sup = pygame.Surface((icone_img.get_width() + txt.get_width() + 6, max(icone_img.get_height(), txt.get_height())), pygame.SRCALPHA)
    sup.blit(icone_img, (0, sup.get_height() // 2 - icone_img.get_height() // 2))
    sup.blit(txt, (icone_img.get_width() + 6, sup.get_height() // 2 - txt.get_height() // 2))
    popups.append([x, y, 0.0, sup])


def desenhar_popups(dt):
    tela = Window.get_screen()
    for pp in popups[:]:
        pp[2] += dt
        if pp[2] >= 1.2:
            popups.remove(pp)
            continue
        sup = pp[3]
        sup.set_alpha(255 if pp[2] < 0.7 else int(255 * (1.2 - pp[2]) / 0.5))
        subida = 50 * (1 - (1 - min(1.0, pp[2] / 0.8)) ** 2)
        tela.blit(sup, (pp[0] - cam.x - sup.get_width() / 2, pp[1] - cam.y - subida - sup.get_height()))


def desenhar_brilhos(dt):
    tela = Window.get_screen()
    for b in brilhos[:]:
        b[2] += dt
        if b[2] >= 0.6:
            brilhos.remove(b)
            continue
        img = BRILHO_QUADROS[int(b[2] / 0.6 * len(BRILHO_QUADROS))]
        tela.blit(img, (b[0] - cam.x - img.get_width() / 2, b[1] - cam.y - img.get_height() / 2 - b[2] * 12))


MAPA_PONTOS = [(10, 164), (36, 146), (62, 140), (92, 118), (120, 112), (150, 128), (178, 116), (204, 86), (230, 78), (258, 44)]
MAPA_NOS = [(36, 146), (92, 118), (150, 128), (204, 86), (258, 44)]
MAPA_MARCOS = [
    (["arvore_enfeitada_0.png", "arvore_enfeitada_2.png", "arvore_enfeitada_1.png", "arvore_enfeitada_2.png"], 0.35),
    (["casa_vila_0.png"], 1.0),
    (["casa.png"], 1.0),
    ([f"livro_{i}.png" for i in range(3)], 0.25),
    ([f"holo_{i}.png" for i in range(8)], 0.1),
]
VEL_MAPA = 55


def curva_catmull(pts, passos=24):
    saida = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(passos):
            t = k / passos
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            saida.append((x * 4, y * 4))
    saida.append((pts[-1][0] * 4, pts[-1][1] * 4))
    return saida


mapa_curva = curva_catmull(MAPA_PONTOS)
mapa_idx_nos = [min(range(len(mapa_curva)), key=lambda k: math.hypot(mapa_curva[k][0] - nx * 4, mapa_curva[k][1] - ny * 4))
                for nx, ny in MAPA_NOS]
mapa_marcos = [Animacao(arqs, dur) for arqs, dur in MAPA_MARCOS]
nivel_liberado = 0
niveis_concluidos = set()
mapa_sel = 0
mapa_pos = float(mapa_idx_nos[0])
mapa_andando = False
mapa_dir = "down"
_teclas = {}
_clique_antes = False


def apertou(*nomes):
    resultado = False
    for nome in nomes:
        agora = teclado.key_pressed(nome)
        if agora and not _teclas.get(nome, False):
            resultado = True
        _teclas[nome] = agora
    return resultado


def clicou():
    global _clique_antes
    agora = mouse.is_button_pressed(1)
    resultado = agora and not _clique_antes
    _clique_antes = agora
    return resultado


def ir_para_mapa(origem, destino):
    global estado, mapa_pos, mapa_sel, mensagem_tempo
    estado = "MAPA"
    mensagem_tempo = 0
    resetar_camera()
    mapa_pos = float(mapa_idx_nos[origem])
    mapa_sel = destino


def posicao_mapa(pos):
    i = int(pos)
    if i >= len(mapa_curva) - 1:
        return mapa_curva[-1]
    f = pos - i
    (x0, y0), (x1, y1) = mapa_curva[i], mapa_curva[i + 1]
    return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f


def atualizar_mapa(dt):
    global mapa_pos, mapa_andando, mapa_dir, mapa_sel, estado
    alvo = mapa_idx_nos[mapa_sel]
    antes = posicao_mapa(mapa_pos)
    if abs(mapa_pos - alvo) > 0.01:
        passo = VEL_MAPA * dt
        if abs(alvo - mapa_pos) <= passo:
            mapa_pos = float(alvo)
        else:
            mapa_pos += passo if alvo > mapa_pos else -passo
        depois = posicao_mapa(mapa_pos)
        dx, dy = depois[0] - antes[0], depois[1] - antes[1]
        if abs(dx) >= abs(dy):
            mapa_dir = "right" if dx > 0 else "left"
        else:
            mapa_dir = "down" if dy > 0 else "up"
        mapa_andando = True
        nico_andar[mapa_dir].avancar(dt)
    else:
        mapa_andando = False
        mapa_dir = "down"
        nico_parado["down"].avancar(dt)
    for m in mapa_marcos:
        m.avancar(dt)

    if apertou("ESC"):
        estado = "MENU"
        return
    if not mapa_andando:
        if apertou("RIGHT", "D", "UP", "W") and mapa_sel < nivel_liberado:
            mapa_sel += 1
        elif apertou("LEFT", "A", "DOWN", "S") and mapa_sel > 0:
            mapa_sel -= 1
        elif apertou("ENTER", "SPACE"):
            iniciar_nivel(mapa_sel)
            estado = "JOGO"
            return
    if clicou():
        mx, my = pygame.mouse.get_pos()
        for i, (nx, ny) in enumerate(MAPA_NOS):
            if i <= nivel_liberado and math.hypot(mx - nx * 4, my - ny * 4 + 30) < 70:
                if i == mapa_sel and not mapa_andando:
                    iniciar_nivel(i)
                    estado = "JOGO"
                    return
                mapa_sel = i


def desenhar_mapa():
    tela = Window.get_screen()
    tela.blit(sprite_arquivo("mapa_fundo.png").image, (0, 0))
    base = sprite_arquivo("no_mapa.png").image
    for i, (nx, ny) in enumerate(MAPA_NOS):
        x, y = nx * 4, ny * 4
        tela.blit(base, (x - base.get_width() // 2, y - base.get_height() // 2))
        marco = mapa_marcos[i].atual().image
        if i > nivel_liberado:
            marco = marco.copy()
            marco.fill((90, 90, 110, 255), special_flags=pygame.BLEND_RGBA_MULT)
        tela.blit(marco, (x - marco.get_width() // 2, y - marco.get_height() - 4))
        if i > nivel_liberado:
            cad = sprite_arquivo("cadeado.png").image
            tela.blit(cad, (x - cad.get_width() // 2, y - cad.get_height() // 2 - 2))
        rotulo = renderizar(f"{i + 1}. {NIVEIS[i]['nome']}", 2, (255, 255, 255) if i <= nivel_liberado else (160, 160, 180))
        tela.blit(rotulo, (x - rotulo.get_width() // 2, y + 30))
        if i in niveis_concluidos:
            estrela = sprite_arquivo("icone_estrela.png").image
            tela.blit(estrela, (x + rotulo.get_width() // 2 + 6, y + 26))
    px, py = posicao_mapa(mapa_pos)
    grupo = nico_andar if mapa_andando else nico_parado
    spr = grupo[mapa_dir].atual().image
    tela.blit(spr, (px - spr.get_width() // 2, py - spr.get_height() + 8))
    if not mapa_andando:
        seta = sprite_arquivo("seta_mapa.png").image
        nx, ny = MAPA_NOS[mapa_sel]
        bob = int(abs(math.sin(tempo_luz * 4)) * 8)
        tela.blit(seta, (nx * 4 - seta.get_width() // 2, ny * 4 - mapa_marcos[mapa_sel].atual().height - 40 - bob))

    faixa = sprite_arquivo("faixa_titulo.png").image
    tela.blit(faixa, (janela.width // 2 - faixa.get_width() // 2, 4))
    titulo = renderizar("MAPA DO NATAL", 5, (255, 206, 70), (60, 10, 18))
    tela.blit(titulo, (janela.width // 2 - titulo.get_width() // 2, 4 + 68 - titulo.get_height() // 2))
    dica = renderizar("SETAS: ANDAR   ENTER: JOGAR   ESC: MENU", 2)
    tela.blit(dica, (janela.width // 2 - dica.get_width() // 2, janela.height - 34))
    if mensagem_tempo > 0:
        desenhar_aviso(128)


carregar_nivel(0)
resetar_camera()

while True:
    atualizar_audio(janela.delta_time())
    if estado == "MENU":
        desenhar_fundo_menu(janela.delta_time())
        desenhar_titulo_menu()

        if (clicou() and mouse.is_over_object(BOTAO_JOGAR)) or apertou("ENTER", "SPACE"):
            ir_para_mapa(mapa_sel, mapa_sel)

    elif estado == "MAPA":
        dt = janela.delta_time()
        tempo_luz += dt
        atualizar_mapa(dt)
        if estado == "MAPA":
            atualizar_neve(dt)
            desenhar_mapa()
            desenhar_neve()
            if mensagem_tempo > 0:
                mensagem_tempo -= dt

    elif estado == "JOGO":
        dt = janela.delta_time()
        janela_dt = dt
        tempo_luz += dt

        magia_natal -= DRENO_MAGIA * dt
        if magia_natal <= 0:
            estado = "DERROTA"
            motivo_derrota = "magia"
            resetar_camera()
            janela.update()
            continue

        if tempo_protegido > 0:
            tempo_protegido -= dt

        if apertou("ESC"):
            if equacao_aberta:
                equacao_aberta = False
            else:
                ir_para_mapa(nivel_atual, nivel_atual)
                janela.update()
                continue

        dx, dy = 0, 0
        if teclado.key_pressed("UP") or teclado.key_pressed("W"): dy -= VEL_NICO * dt
        if teclado.key_pressed("DOWN") or teclado.key_pressed("S"): dy += VEL_NICO * dt
        if teclado.key_pressed("LEFT") or teclado.key_pressed("A"): dx -= VEL_NICO * dt
        if teclado.key_pressed("RIGHT") or teclado.key_pressed("D"): dx += VEL_NICO * dt
        if equacao_aberta:
            dx, dy = 0, 0
        if dx < 0:
            nico_dir = "left"
        elif dx > 0:
            nico_dir = "right"
        elif dy < 0:
            nico_dir = "up"
        elif dy > 0:
            nico_dir = "down"

        antes_x, antes_y = nico_x, nico_y
        if dx != 0:
            cx_novo = nico_x + dx
            if not bloqueado(*caixa_nico(cx_novo, nico_y)):
                nico_x = cx_novo
        if dy != 0:
            cy_novo = nico_y + dy
            if not bloqueado(*caixa_nico(nico_x, cy_novo)):
                nico_y = cy_novo
        andando = nico_x != antes_x or nico_y != antes_y
        grupo = nico_andar if andando else nico_parado
        grupo[nico_dir].avancar(dt)
        nico_atual = grupo[nico_dir].atual()
        nico_atual.set_position(nico_x, nico_y)

        ncx = nico_x + NICO_W / 2
        ncy = nico_y + NICO_H / 2

        tile_nico = tile_de(ncx, ncy)
        if bloqueio_alcapao:
            if tile_nico not in alcapoes:
                bloqueio_alcapao = False
        elif alcapoes.get(tile_nico):
            if subterraneo:
                tocar("sfx_entrar")
                sair_subterraneo()
            else:
                tocar("sfx_entrar")
                entrar_subterraneo(tile_nico)
            janela.update()
            continue

        cam.follow(nico_atual)
        atualizar_neve(dt)

        if not subterraneo:
            for rn in renas:
                rn.atualizar(dt)
            for e in elfos[:]:
                e.atualizar(dt)
                if e.morto and e.tempo_morte >= DURACAO_MORTE_ELFO:
                    elfos.remove(e)

        desenhar_mundo()

        for c in chaves[:]:
            desenhar_coletavel(c, "chave.png")
            if math.hypot(c.x + 16 - ncx, c.y + 16 - ncy) < RAIO_COLETA:
                inventario_chaves += 1
                tocar("sfx_chave")
                chaves.remove(c)
                popup(c.x + 16, c.y, "icone_chave.png", "+1", (255, 226, 120))

        for m in moedas[:]:
            desenhar_coletavel(m, "moeda.png")
            if math.hypot(m.x + 16 - ncx, m.y + 16 - ncy) < RAIO_COLETA:
                moedas_coletadas += 1
                tocar("sfx_moeda")
                magia_natal = min(MAGIA_INICIAL, magia_natal + MAGIA_MOEDA)
                moedas.remove(m)
                popup(m.x + 16, m.y, "icone_estrela.png", f"+{MAGIA_MOEDA}", (130, 220, 255))

        for p in pocoes[:]:
            desenhar_coletavel(p, "pocao.png")
            if math.hypot(p.x + 16 - ncx, p.y + 18 - ncy) < RAIO_COLETA:
                magia_natal = min(MAGIA_INICIAL, magia_natal + MAGIA_POCAO)
                tocar("sfx_pocao")
                pocoes.remove(p)
                popup(p.x + 16, p.y, "icone_estrela.png", f"+{MAGIA_POCAO}", (130, 220, 255))

        concluiu = False
        for f in fragmentos[:]:
            desenhar_coletavel(f, "fragmento.png")
            if math.hypot(f.x + 16 - ncx, f.y + 16 - ncy) < RAIO_COLETA:
                fragmentos_coletados += 1
                tocar("sfx_fragmento")
                magia_natal = min(MAGIA_INICIAL, magia_natal + RECUPERA_FRAGMENTO)
                fragmentos.remove(f)
                popup(f.x + 16, f.y, "fragmento.png", f"{fragmentos_coletados}/{fragmentos_total}", (255, 150, 255))
                mostrar("Fragmento coletado!")
                if fragmentos_coletados >= fragmentos_total:
                    if livro_tile is None:
                        concluiu = True
                    else:
                        mostrar("Todos os fragmentos! Vá até o livro.")

        desenhar_brilhos(dt)

        if equacao_aberta:
            ler_digitacao()
            if erro_tempo > 0:
                erro_tempo -= dt
            if apertou("ENTER", pygame.K_KP_ENTER) and resposta not in ("", "-"):
                if int(resposta) in equacao[1]:
                    equacao_aberta = False
                    tocar("sfx_acerto")
                    concluiu = True
                else:
                    magia_natal -= 10
                    tocar("sfx_erro")
                    erro_tempo = 1.5
                    resposta = ""
        elif apertou("E") and perto_do_livro():
            if fragmentos_coletados >= fragmentos_total:
                equacao_aberta = True
                resposta = ""
                erro_tempo = 0.0
            else:
                mostrar("Pegue todos os fragmentos primeiro!")

        if concluiu:
            niveis_concluidos.add(nivel_atual)
            if nivel_atual + 1 < len(NIVEIS):
                nivel_liberado = max(nivel_liberado, nivel_atual + 1)
                ir_para_mapa(nivel_atual, nivel_atual + 1)
                mostrar(f"Nível {nivel_atual + 2} liberado!")
            else:
                estado = "VITORIA"
                resetar_camera()
            janela.update()
            continue

        if teclado.key_pressed("E"):
            trancados = list(portas_set) + [t for t, aberto in alcapoes.items() if not aberto]
            proximas = sorted(trancados, key=lambda t: math.hypot(
                t[0] * TAMANHO_TILE + 32 - ncx, t[1] * TAMANHO_TILE + 32 - ncy))
            if proximas:
                porta = proximas[0]
                if math.hypot(porta[0] * TAMANHO_TILE + 32 - ncx,
                              porta[1] * TAMANHO_TILE + 32 - ncy) < RAIO_PORTA:
                    if inventario_chaves > 0:
                        inventario_chaves -= 1
                        if porta in alcapoes:
                            alcapoes[porta] = True
                            bloqueio_alcapao = True
                            mostrar("O alçapão foi destrancado!")
                        else:
                            portas_set.discard(porta)
                            mostrar("Porta aberta!")
                    elif porta in alcapoes:
                        mostrar("Este alçapão precisa de uma chave.")
                    else:
                        mostrar("Esta porta precisa de uma chave.")

        if subterraneo:
            nico_atual.draw()
        else:
            antes_bx, antes_by = boss_cx, boss_cy
            mover_papai(dt)
            if boss_cx - antes_bx > 0.01:
                papai_dir = "dir"
            elif boss_cx - antes_bx < -0.01:
                papai_dir = "esq"
            if math.hypot(boss_cx - antes_bx, boss_cy - antes_by) > 0.01:
                papai_andar[papai_dir].avancar(dt)
                papai_atual = papai_andar[papai_dir].atual()
            else:
                papai_parado.avancar(dt)
                papai_atual = papai_parado.atual()
            papai_atual.set_position(boss_cx - papai_atual.width / 2, boss_cy - papai_atual.height / 2)

            caixa_boss = (boss_cx - HITBOX_PAPAI[0] / 2, boss_cy - HITBOX_PAPAI[1] / 2,
                          HITBOX_PAPAI[0], HITBOX_PAPAI[1])
            for e in elfos_vivos():
                caixa_elfo = (e.cx - HITBOX_ELFO[0] / 2, e.cy - HITBOX_ELFO[1] / 2,
                              HITBOX_ELFO[0], HITBOX_ELFO[1])
                if sobrepoe(caixa_boss, caixa_elfo):
                    e.morrer()
                    tocar("sfx_elfo")
                    pausa_papai = PAUSA_APOS_PEGAR_ELFO
                    caminho_boss = []
                    mostrar("Um elfo foi pego pelo Papai!")

            for rn in renas:
                rn.desenhar()
            for e in elfos:
                e.desenhar()
            papai_atual.draw()
            nico_atual.draw()

            if not elfos_vivos():
                estado = "DERROTA"
                motivo_derrota = "elfos"
                resetar_camera()
                janela.update()
                continue

            if tempo_protegido <= 0 and sobrepoe(caixa_boss, caixa_nico(nico_x, nico_y)):
                nico_x = spawn_tile[0] * TAMANHO_TILE + TAMANHO_TILE / 2 - NICO_W / 2
                nico_y = spawn_tile[1] * TAMANHO_TILE + TAMANHO_TILE / 2 - NICO_H / 2
                nico_atual.set_position(nico_x, nico_y)
                boss_cx, boss_cy = centro_tile(boss_tile_inicial)
                caminho_boss = []
                rota_idx = 0
                magia_natal -= PENALIDADE_CAPTURA
                tempo_protegido = PROTECAO_APOS_CAPTURA
                equacao_aberta = False
                resposta = ""
                tocar("sfx_nico_pego")
                mostrar("O Papai Cruel te pegou!")

        if subterraneo:
            desenhar_escuridao(dt)
        else:
            desenhar_neve()
            if tema_atual == "tarde":
                aplicar_por_do_sol()
            elif tema_atual == "noite":
                desenhar_escuridao(dt, 175, (6, 8, 30))
        desenhar_popups(dt)
        desenhar_aviso_livro()
        desenhar_hud()
        if equacao_aberta:
            desenhar_equacao()
        if mensagem_tempo > 0:
            mensagem_tempo -= dt

    elif estado == "DERROTA":
        if motivo_derrota == "elfos":
            tela_final("OS ELFOS FORAM TODOS ELIMINADOS!", (255, 70, 70), "CLIQUE: TENTAR DE NOVO    ESC: MAPA")
        else:
            tela_final("O NATAL FOI CANCELADO!", (255, 70, 70), "CLIQUE: TENTAR DE NOVO    ESC: MAPA")
        if apertou("ESC"):
            ir_para_mapa(nivel_atual, nivel_atual)
        elif clicou():
            iniciar_nivel(nivel_atual)
            estado = "JOGO"

    elif estado == "VITORIA":
        tela_final("VOCÊ SALVOU O NATAL!", (255, 230, 60), "Clique para voltar ao menu")
        if clicou():
            estado = "MENU"
            resetar_camera()

    janela.update()
