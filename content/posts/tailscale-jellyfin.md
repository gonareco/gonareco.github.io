---
title: "Cómo liberé mi Jellyfin de la red local"
date: 2026-05-29
tags: ["Tailscale", "VPN", "Jellyfin", "Linux", "Fedora", "Podman"]
---

## El problema: esclavo de mi propia red

Tenía Jellyfin corriendo en mi Lenovo. En casa perfecto, pero apenas salía de mi red local, por supuesto me quedaba sin mis series de lujo y la mejor película de todos los tiempos (Simpsons en formato 4:3, South Park y Terminator II (Versión Extendida))

Necesitaba una forma de acceder desde cualquier lugar, pero quería evitar configuraciones de router, puertos, certificados y esas cosas porque desde mi punto de vista (el único que importa para el caso) no ameritaba el esfuerzo de configuraciones para algo tan hogareño.
Ojo, una alternativa DIY (Do It Yourself, lo aclaro más abajo) es completamente válida, será material para otro post.

## La solución: Tailscale

Una VPN mesh de una simpleza asombrosa, no necesitamos: 
- Tocar el router
- Abrir puertos

Además ofrece:
- Encriptado por defecto
- Gratis para uso personal

## ¿Por qué no WireGuard (DIY)?

Podría haberlo hecho a mano. WireGuard es excelente, pero requiere generar claves, escribir los `.conf` y que tu ISP no te tenga detrás de una CGNAT. No tenia ganas de hablar con Telecentro para esto. Tailscale es WireGuard, pero con toda la parte tediosa automatizada.

## Instalación en la Lenovo (Fedora) justo donde está corriendo Jellyfin.

    bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up

El comando te da un enlace. Lo abrís, iniciás sesión (con Google, GitHub, lo que tengas) y listo.
La Lenovo ya tiene una IP fija dentro de la red de Tailscale (algo como 100.x.x.x).

Después, para habilitar el servicio:

    bash
    sudo systemctl enable tailscaled

> Después de instalar Tailscale, hay que habilitar el servicio para que arranque automáticamente con el sistema. Si no, cada vez que reinicies la Lenovo vas a tener que volver a correr tailscale up.

Verificás:

    bash
    tailscale ip -4
    # 100.xxx.xxx.xxx (la ip que te da)

## El problema con Jellyfin (y la solución)

Jellyfin, por defecto, solo considera "red local" a tu rango de casa (192.168.x.x). La IP de Tailscale (100.xxx.xxx.xxx) es una red diferente, así que Jellyfin la trata como si fuera externa y no la ve.

Para arreglarlo, en la web de Jellyfin (digamos en tu Jellyfin local, desde el Tablero administrador)
> Administrador → Red → Redes LAN

Ahí pegué:

    text
    192.168.0.0/24, 100.64.0.0/10

Guardé, reinicié Jellyfin, y listo.
La IP de Tailscale pasó a ser "local".

## Compartir el acceso (sin compartir mi cuenta)

Para que alguien más pueda ver mi contenido desde cualquier sitio hay que compartir desde Tailscale un enlace (parecido a compartir un documento desde Google Drive)

En la consola de Tailscale, fui a la Lenovo → tres puntos → "Share...".
Generé un enlace y se lo mandé.
Se crea una cuenta gratuita, (cero costo), se acepta el enlace, agrega el dispositivo para compartir la red con mi Lenovo y listo.

El límite de 3 usuarios de Tailscale no aplica al "Share". Esos serían usuarios con permisos de admin y por el momento esto lo administro yo solo.
Podría compartirlo con varias personas y cada una usa su propia cuenta. La única (y gran limitación, es mi propio hardware, el streaming de mas de 3 series o en alta calidad dispara el uso del procesador)

## La app oficial de Jellyfin en el celular

Con Tailscale activado en el teléfono, la app oficial conectó sin problemas.
Solo tuve que agregar el servidor manualmente con la IP de Tailscale: http://100.xxx.xxx.xxx:8096.

## Verificación final

En la Lenovo, con Tailscale activo:

    bash
    tailscale status
    100.xxx.xxx.xxx  fedora          gonareco@  linux  active
    100.xxx.xxx.xxx    gonzalo-motorola   gonareco@  android  active

Desde el celular (con Tailscale activado), abrís la app de Jellyfin → y aparece. Como si estuviera en mi casa.

## ¿Vale la pena?

Absolutamente.
* No toqué el router.
* No abrí un solo puerto.
* Tengo un capítulo de los Simpsons siempre disponible, en formato 4:3 sin depender de pagarle a Disney.

## Lo que aprendí
* Tailscale es la forma más fácil de VPN sin volverse loco.
* Jellyfin necesita que le digas qué redes son "seguras".