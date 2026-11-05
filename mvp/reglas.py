"""Reglas simples del MVP de Tres60 SafeCampus.

Toda la lógica de detección de situaciones vive aquí y no depende de la
cámara ni del modelo: recibe detecciones (clase, confianza, caja) y la hora,
y devuelve alertas y textos de estado para dibujar. Así se puede probar sin
video (ver tests/test_reglas.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

Caja = tuple[float, float, float, float]  # x1, y1, x2, y2 en píxeles


@dataclass
class Deteccion:
    clase: str
    confianza: float
    caja: Caja


@dataclass
class Alerta:
    tipo: str
    mensaje: str
    cajas: list[Caja]
    duracion: float = 0.0  # segundos desde que empezó la situación hasta la alerta


@dataclass
class Estado:
    """Texto que se dibuja sobre el video (por ejemplo, un contador)."""

    texto: str
    caja: Caja | None = None
    alerta: bool = False  # True cuando la regla ya disparó para este caso


# ---------------------------------------------------------------- utilidades


def iou(a: Caja, b: Caja) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def se_tocan(a: Caja, b: Caja) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def centro(c: Caja) -> tuple[float, float]:
    return (c[0] + c[2]) / 2, (c[1] + c[3]) / 2


def ampliar(c: Caja, factor: float) -> Caja:
    """Agranda la caja `factor` veces su propio tamaño hacia cada lado."""
    w, h = c[2] - c[0], c[3] - c[1]
    return c[0] - w * factor, c[1] - h * factor, c[2] + w * factor, c[3] + h * factor


class Temporizador:
    """Mide cuánto tiempo lleva cumpliéndose una condición.

    Si la condición deja de cumplirse por menos de `tolerancia_s` segundos
    (por ejemplo, el modelo pierde a la persona en un fotograma), el conteo
    no se reinicia.
    """

    def __init__(self, tolerancia_s: float = 1.0):
        self.tolerancia_s = tolerancia_s
        self.inicio: float | None = None
        self.ultimo_ok: float | None = None

    def actualizar(self, cumple: bool, ahora: float) -> float:
        if cumple:
            if self.inicio is None:
                self.inicio = ahora
            self.ultimo_ok = ahora
        elif self.inicio is not None and ahora - self.ultimo_ok > self.tolerancia_s:
            self.reiniciar()
        return self.duracion()

    def duracion(self) -> float:
        if self.inicio is None:
            return 0.0
        return self.ultimo_ok - self.inicio

    @property
    def activo(self) -> bool:
        return self.inicio is not None

    def reiniciar(self) -> None:
        self.inicio = None
        self.ultimo_ok = None


@dataclass
class Pista:
    """Un objeto o persona seguido entre fotogramas."""

    id: int
    caja: Caja
    visto: float
    ancla: Caja  # posición donde quedó quieto (para objetos)
    temporizador: Temporizador
    alertado: bool = False


class Seguidor:
    """Seguimiento mínimo por solapamiento (IoU) entre fotogramas.

    Basta para objetos quietos y personas que se mueven poco, que es lo que
    necesitan estas reglas. Las pistas que no se ven durante `olvido_s`
    segundos se eliminan.
    """

    def __init__(self, tolerancia_s: float, olvido_s: float = 3.0, iou_min: float = 0.3):
        self.tolerancia_s = tolerancia_s
        self.olvido_s = olvido_s
        self.iou_min = iou_min
        self.pistas: dict[int, Pista] = {}
        self._ids = count(1)

    def cambiar_tolerancia(self, tolerancia_s: float) -> None:
        self.tolerancia_s = tolerancia_s
        for pista in self.pistas.values():
            pista.temporizador.tolerancia_s = tolerancia_s

    def actualizar(self, cajas: list[Caja], ahora: float) -> list[Pista]:
        libres = dict(self.pistas)
        vistas: list[Pista] = []
        for caja in sorted(cajas, key=lambda c: -(c[2] - c[0]) * (c[3] - c[1])):
            mejor, mejor_iou = None, self.iou_min
            for pista in libres.values():
                v = iou(caja, pista.caja)
                if v >= mejor_iou:
                    mejor, mejor_iou = pista, v
            if mejor is None:
                mejor = Pista(next(self._ids), caja, ahora, caja, Temporizador(self.tolerancia_s))
                self.pistas[mejor.id] = mejor
            else:
                del libres[mejor.id]
                mejor.caja, mejor.visto = caja, ahora
            vistas.append(mejor)
        for pista in libres.values():
            if ahora - pista.visto > self.olvido_s:
                del self.pistas[pista.id]
        return vistas


def _mmss(segundos: float) -> str:
    s = int(segundos)
    return f"{s // 60:02d}:{s % 60:02d}"


# ------------------------------------------------------------------- reglas


class ReglaAglomeracion:
    """Muchas personas a la vez durante cierto tiempo."""

    tipo = "aglomeracion"

    def __init__(self, **params):
        self.temporizador = Temporizador(1.5)
        self.alertado = False
        self.configurar(**{"personas_min": 4, "segundos": 5, **params})

    def configurar(self, personas_min=None, segundos=None, tolerancia_s=None):
        """Cambia parámetros sin perder el estado (se usa al ajustar desde el dashboard)."""
        if personas_min is not None:
            self.personas_min = int(personas_min)
        if segundos is not None:
            self.segundos = float(segundos)
        if tolerancia_s is not None:
            self.temporizador.tolerancia_s = float(tolerancia_s)

    def evaluar(self, personas: list[Deteccion], objetos, ancho, alto, ahora):
        n = len(personas)
        dur = self.temporizador.actualizar(n >= self.personas_min, ahora)
        if not self.temporizador.activo:
            self.alertado = False
        alertas = []
        if dur >= self.segundos and not self.alertado:
            self.alertado = True
            alertas.append(
                Alerta(
                    self.tipo,
                    f"Aglomeración: {n} personas durante {dur:.0f} s "
                    f"(umbral: {self.personas_min} personas, {self.segundos:.0f} s)",
                    [p.caja for p in personas],
                    dur,
                )
            )
        texto = f"Personas: {n} / {self.personas_min}"
        if self.temporizador.activo:
            texto += f"  ({dur:.0f}/{self.segundos:.0f} s)"
        return alertas, [Estado(texto, alerta=self.alertado)]


class ReglaObjetoDesatendido:
    """Mochila, bolso o maleta sin ninguna persona cerca durante cierto tiempo.

    Hipótesis del proyecto: el conteo empieza cuando no hay nadie en el lugar
    del objeto (su caja ampliada), y si llega a `segundos` (10 min en la
    hipótesis real) se genera la alerta. Si una persona se queda junto al
    objeto más de `segundos_para_reiniciar`, se considera que volvió el dueño
    y el conteo se reinicia. Si el objeto se mueve, también se reinicia.
    """

    tipo = "objeto_desatendido"

    def __init__(self, **params):
        self.seguidor = Seguidor(tolerancia_s=3.0, olvido_s=5.0)
        defaults = {
            "clases": ("backpack", "handbag", "suitcase"),
            "segundos": 600,
            "margen": 1.0,
            "segundos_para_reiniciar": 3.0,
            "movimiento_max": 0.5,
        }
        self.configurar(**{**defaults, **params})

    def configurar(self, clases=None, segundos=None, margen=None,
                   segundos_para_reiniciar=None, movimiento_max=None):
        if clases is not None:
            self.clases = set(clases)
        if segundos is not None:
            self.segundos = float(segundos)
        if margen is not None:
            self.margen = float(margen)
        if movimiento_max is not None:
            self.movimiento_max = float(movimiento_max)
        if segundos_para_reiniciar is not None:
            self.seguidor.cambiar_tolerancia(float(segundos_para_reiniciar))

    def evaluar(self, personas, objetos: list[Deteccion], ancho, alto, ahora):
        cajas = [o.caja for o in objetos if o.clase in self.clases]
        alertas, estados = [], []
        for pista in self.seguidor.actualizar(cajas, ahora):
            # Si el objeto se desplazó más de `movimiento_max` veces su tamaño, alguien lo movió.
            (cx, cy), (ax, ay) = centro(pista.caja), centro(pista.ancla)
            tam = max(pista.ancla[2] - pista.ancla[0], pista.ancla[3] - pista.ancla[1])
            if abs(cx - ax) > tam * self.movimiento_max or abs(cy - ay) > tam * self.movimiento_max:
                pista.ancla = pista.caja
                pista.temporizador.reiniciar()
                pista.alertado = False

            zona = ampliar(pista.caja, self.margen)
            alguien_cerca = any(se_tocan(zona, p.caja) for p in personas)
            dur = pista.temporizador.actualizar(not alguien_cerca, ahora)
            if not pista.temporizador.activo:
                pista.alertado = False

            if dur >= self.segundos and not pista.alertado:
                pista.alertado = True
                alertas.append(
                    Alerta(
                        self.tipo,
                        f"Objeto #{pista.id} sin persona cerca durante {_mmss(dur)} "
                        f"(umbral: {_mmss(self.segundos)})",
                        [pista.caja],
                        dur,
                    )
                )
            if pista.temporizador.activo:
                txt = f"Objeto #{pista.id} solo {_mmss(dur)}/{_mmss(self.segundos)}"
            else:
                txt = f"Objeto #{pista.id} acompañado"
            estados.append(Estado(txt, pista.caja, pista.alertado))
        return alertas, estados


class ReglaPersonaEnSuelo:
    """Persona en posición horizontal durante cierto tiempo.

    Criterio simple: la caja de la persona es más ancha que alta
    (`proporcion` = ancho / alto). Se ignoran las cajas que tocan el borde
    inferior del video, porque una persona muy cerca del celular (solo cabeza
    y hombros) también produce una caja ancha.
    """

    tipo = "persona_en_suelo"

    def __init__(self, **params):
        self.seguidor = Seguidor(tolerancia_s=1.5, olvido_s=3.0, iou_min=0.2)
        defaults = {"segundos": 30, "proporcion": 1.3, "ignorar_borde_inferior": True}
        self.configurar(**{**defaults, **params})

    def configurar(self, segundos=None, proporcion=None, ignorar_borde_inferior=None,
                   tolerancia_s=None):
        if segundos is not None:
            self.segundos = float(segundos)
        if proporcion is not None:
            self.proporcion = float(proporcion)
        if ignorar_borde_inferior is not None:
            self.ignorar_borde_inferior = bool(ignorar_borde_inferior)
        if tolerancia_s is not None:
            self.seguidor.cambiar_tolerancia(float(tolerancia_s))

    def evaluar(self, personas: list[Deteccion], objetos, ancho, alto, ahora):
        alertas, estados = [], []
        for pista in self.seguidor.actualizar([p.caja for p in personas], ahora):
            x1, y1, x2, y2 = pista.caja
            horizontal = (x2 - x1) >= self.proporcion * max(1.0, y2 - y1)
            if self.ignorar_borde_inferior and y2 >= alto * 0.98:
                horizontal = False
            dur = pista.temporizador.actualizar(horizontal, ahora)
            if not pista.temporizador.activo:
                pista.alertado = False
            if dur >= self.segundos and not pista.alertado:
                pista.alertado = True
                alertas.append(
                    Alerta(
                        self.tipo,
                        f"Persona #{pista.id} en el suelo durante {dur:.0f} s "
                        f"(umbral: {self.segundos:.0f} s)",
                        [pista.caja],
                        dur,
                    )
                )
            if pista.temporizador.activo:
                estados.append(
                    Estado(f"En el suelo {dur:.0f}/{self.segundos:.0f} s", pista.caja, pista.alertado)
                )
        return alertas, estados


class ReglaZonaRestringida:
    """Persona con los pies dentro de un rectángulo durante cierto tiempo.

    `zona` va en proporciones del video: [x1, y1, x2, y2] entre 0 y 1.
    """

    tipo = "zona_restringida"

    def __init__(self, **params):
        self.seguidor = Seguidor(tolerancia_s=1.0, olvido_s=2.0, iou_min=0.2)
        self.configurar(**{"zona": (0.6, 0.0, 1.0, 1.0), "segundos": 2, **params})

    def configurar(self, zona=None, segundos=None, tolerancia_s=None):
        if zona is not None:
            self.zona = tuple(float(v) for v in zona)
        if segundos is not None:
            self.segundos = float(segundos)
        if tolerancia_s is not None:
            self.seguidor.cambiar_tolerancia(float(tolerancia_s))

    def evaluar(self, personas: list[Deteccion], objetos, ancho, alto, ahora):
        zx1, zy1, zx2, zy2 = (
            self.zona[0] * ancho, self.zona[1] * alto, self.zona[2] * ancho, self.zona[3] * alto
        )
        alertas = []
        estados = [Estado("Zona restringida", (zx1, zy1, zx2, zy2))]
        for pista in self.seguidor.actualizar([p.caja for p in personas], ahora):
            pie_x, pie_y = (pista.caja[0] + pista.caja[2]) / 2, pista.caja[3]
            dentro = zx1 <= pie_x <= zx2 and zy1 <= pie_y <= zy2
            dur = pista.temporizador.actualizar(dentro, ahora)
            if not pista.temporizador.activo:
                pista.alertado = False
            if dur >= self.segundos and not pista.alertado:
                pista.alertado = True
                alertas.append(
                    Alerta(self.tipo, f"Persona #{pista.id} en zona restringida durante {dur:.0f} s",
                           [pista.caja], dur)
                )
            if pista.temporizador.activo:
                estados.append(Estado(f"En zona {dur:.0f} s", pista.caja, pista.alertado))
        return alertas, estados


# -------------------------------------------------------------------- motor

REGLAS = {
    "aglomeracion": ReglaAglomeracion,
    "objeto_desatendido": ReglaObjetoDesatendido,
    "persona_en_suelo": ReglaPersonaEnSuelo,
    "zona_restringida": ReglaZonaRestringida,
}


@dataclass
class Motor:
    """Aplica todas las reglas activas a cada fotograma."""

    reglas: list = field(default_factory=list)

    @classmethod
    def desde_config(cls, config_reglas: dict) -> "Motor":
        motor = cls()
        motor.aplicar_config(config_reglas)
        return motor

    def aplicar_config(self, config_reglas: dict) -> None:
        """Activa, desactiva o ajusta reglas sin perder el estado de las que siguen activas."""
        actuales = {r.tipo: r for r in self.reglas}
        nuevas = []
        for nombre, params in (config_reglas or {}).items():
            if nombre not in REGLAS:
                raise ValueError(f"Regla desconocida: {nombre}")
            params = dict(params or {})
            if not params.pop("activa", True):
                continue
            if nombre in actuales:
                actuales[nombre].configurar(**params)
                nuevas.append(actuales[nombre])
            else:
                nuevas.append(REGLAS[nombre](**params))
        self.reglas = nuevas

    def evaluar(self, detecciones: list[Deteccion], ancho: int, alto: int, ahora: float):
        personas = [d for d in detecciones if d.clase == "person"]
        objetos = [d for d in detecciones if d.clase != "person"]
        alertas, estados = [], []
        for regla in self.reglas:
            a, e = regla.evaluar(personas, objetos, ancho, alto, ahora)
            alertas += a
            estados += e
        return alertas, estados
