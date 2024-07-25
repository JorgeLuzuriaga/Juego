import pygame
import random

pygame.init()
pygame.mixer.init()

fondo = pygame.image.load("images/fondo.png")
sonido_laser = pygame.mixer.Sound("sounds/laser.wav")
sonido_explosion = pygame.mixer.Sound("sounds/explosion.wav")
sonido_golpe = pygame.mixer.Sound("sounds/golpe.wav")

lista_explosiones = []
for i in range(1, 13):
    explosion = pygame.image.load(f"explosiones/{i}.png")
    lista_explosiones.append(explosion)

ancho = fondo.get_width()
alto = fondo.get_height()
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("ALIENS 2.0")
ejecutar = True
fps = 60
reloj = pygame.time.Clock()
puntaje = 0
vida = 100
blanco = (255, 255, 255)
negro = (0, 0, 0)

def texto_puntuacion(frame, texto, tamaño, x, y):
    fuente = pygame.font.SysFont("Small Fonts", tamaño, bold=True)
    texto_frame = fuente.render(texto, True, blanco, negro)
    rect_texto = texto_frame.get_rect()
    rect_texto.midtop = (x, y)
    frame.blit(texto_frame, rect_texto)

def barra_vida(frame, x, y, nivel):
    longitud = 100
    alto = 20
    fill = int((nivel / 100) * longitud)
    borde = pygame.Rect(x, y, longitud, alto)
    fill = pygame.Rect(x, y, fill, alto)
    pygame.draw.rect(frame, (255, 0, 55), fill)
    pygame.draw.rect(frame, negro, borde, 4)

class Personaje(pygame.sprite.Sprite):
    def __init__(self, imagen_path, x, y, velocidad):
        super().__init__()
        self.image = pygame.image.load(imagen_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.velocidad_x = 0
        self.velocidad_y = velocidad
        self.vida = 100

    def update(self):
        self.rect.x += self.velocidad_x
        self.rect.y += self.velocidad_y
        if self.rect.right > ancho:
            self.rect.right = ancho
        elif self.rect.left < 0:
            self.rect.left = 0

class Jugador(Personaje):
    def __init__(self):
        super().__init__("images/A1.png", ancho // 2, alto - 50, 0)
        pygame.display.set_icon(self.image)

    def update(self):
        self.velocidad_x = 0
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.velocidad_x = -5
        elif teclas[pygame.K_RIGHT]:
            self.velocidad_x = 5

        self.rect.x += self.velocidad_x
        if self.rect.right > ancho:
            self.rect.right = ancho
        elif self.rect.left < 0:
            self.rect.left = 0

    def disparar(self):
        bala = BalaJugador(self.rect.centerx, self.rect.top)
        grupo_jugador.add(bala)
        grupo_balas_jugador.add(bala)
        sonido_laser.play()

class Enemigo(Personaje):
    def __init__(self, x, y):
        super().__init__("images/E1.png", x, y, random.randrange(-5, 20))

    def update(self):
        self.rect.x += 4
        if self.rect.x >= ancho:
            self.rect.x = 0
            self.rect.y += 50

    def disparar(self):
        bala = BalaEnemigo(self.rect.centerx, self.rect.bottom)
        grupo_jugador.add(bala)
        grupo_balas_enemigos.add(bala)
        sonido_laser.play()

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, imagen_path, velocidad):
        super().__init__()
        self.image = pygame.image.load(imagen_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = y
        self.velocidad = velocidad

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0 or self.rect.top > alto:
            self.kill()

class BalaJugador(Bala):
    def __init__(self, x, y):
        super().__init__(x, y, "images/B2.png", -18)

class BalaEnemigo(Bala):
    def __init__(self, x, y):
        super().__init__(x, y, "images/B1.png", 4)
        self.image = pygame.transform.rotate(self.image, 180)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, posicion):
        super().__init__()
        self.image = lista_explosiones[0]
        self.rect = self.image.get_rect()
        self.rect.center = posicion
        self.tiempo = pygame.time.get_ticks()
        self.velocidad_explosion = 30
        self.frames = 0

    def update(self):
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.tiempo > self.velocidad_explosion:
            self.tiempo = tiempo_actual
            self.frames += 1
            if self.frames == len(lista_explosiones):
                self.kill()
            else:
                posicion = self.rect.center
                self.image = lista_explosiones[self.frames]
                self.rect = self.image.get_rect()
                self.rect.center = posicion

grupo_jugador = pygame.sprite.Group()
grupo_enemigos = pygame.sprite.Group()
grupo_balas_jugador = pygame.sprite.Group()
grupo_balas_enemigos = pygame.sprite.Group()

jugador = Jugador()
grupo_jugador.add(jugador)

for _ in range(15):
    enemigo = Enemigo(random.randrange(1, ancho - 50), 10)
    grupo_enemigos.add(enemigo)
    grupo_jugador.add(enemigo)

while ejecutar:
    reloj.tick(fps)
    ventana.blit(fondo, (0, 0))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutar = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                jugador.disparar()

    grupo_jugador.update()
    grupo_enemigos.update()
    grupo_balas_jugador.update()
    grupo_balas_enemigos.update()

    grupo_jugador.draw(ventana)

    colision1 = pygame.sprite.groupcollide(grupo_enemigos, grupo_balas_jugador, True, True)
    for enemigo in colision1:
        puntaje += 10
        enemigo.disparar()
        nuevo_enemigo = Enemigo(random.randrange(1, ancho - 50), 10)
        grupo_enemigos.add(nuevo_enemigo)
        grupo_jugador.add(nuevo_enemigo)
        explosion = Explosion(enemigo.rect.center)
        grupo_jugador.add(explosion)
        sonido_explosion.set_volume(0.3)
        sonido_explosion.play()

    colision2 = pygame.sprite.spritecollide(jugador, grupo_balas_enemigos, True)
    for bala in colision2:
        jugador.vida -= 10
        if jugador.vida <= 0:
            ejecutar = False
        explosion = Explosion(bala.rect.center)
        grupo_jugador.add(explosion)
        sonido_golpe.play()

    colision3 = pygame.sprite.spritecollide(jugador, grupo_enemigos, False)
    for enemigo in colision3:
        jugador.vida -= 100
        nuevo_enemigo = Enemigo(random.randrange(1, ancho - 50), 10)
        grupo_enemigos.add(nuevo_enemigo)
        grupo_jugador.add(nuevo_enemigo)
        if jugador.vida <= 0:
            ejecutar = False

    texto_puntuacion(ventana, f"SCORE: {puntaje}", 30, ancho - 85, 2)
    barra_vida(ventana, ancho - 285, 0, jugador.vida)

    pygame.display.flip()

pygame.quit()
