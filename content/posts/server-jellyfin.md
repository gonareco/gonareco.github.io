---
title: "Cómo convertí un caro pisapapeles en un servidor media casero (con Fedora, Podman y Jellyfin)"
date: 2026-05-19
tags: ["Linux", "Fedora", "Podman", "Jellyfin", "SELinux", "Permisos"]
---

## El problema: Una Lenovo que adoro, que anda muy bien pero ya tiene sus años (11)

Mi vieja Lenovo es un i7 6500, con 16 GB de RAM, un SSD de 256 y un HDD de 1 TB. ¿Sistema operativo? Fedora, desde ya.
Para ahorrarnos de decirle *la vieja*, *la nueva* etc, la llamaremos cariñosamente **Jelly**.

Como Jelly estaba apagada acumulando polvo siendo un *pisapapeles caro* decidí darle una segunda vida y de paso aprender y compartir algo.

Dentro de las posibilidades que había siempre me pareció interesante tener un propio servidor local de series (que ya bajé de la manera más legal posible, por supuesto).
Actualmente las tengo en ese disco de 1 TB y las veo mediante DLNA y accedo desde la TV.
Su visualización es bastante *tradicional* por decirlo amablemente ya que es una vista de carpetas y archivos muy de vieja escuela (no tengo nada en contra de eso).

De todos modos, era hora de probar Jellyfin y de paso darle una nueva vida al equipo apagado desde hacía meses.

## Primeros pasos

**Importante:** Actualizar el SO al día de hoy. La cosa cambia muy rápido y justamente hace 2 o 3 semanas (escribo esto el 19 de mayo de 2026), salió una crítica vulnerabilidad en el kernel de Linux por lo que estar actualizado al día es más importante que nunca.

Actualizar primero Fedora de su versión 42, que es la que tenía el equipo, a la última vigente. 

    bash
    sudo dnf upgrade --refresh
    sudo dnf install dnf-plugin-system-upgrade # es el asistente de instalación oficial y mejora la experiencia de cambio entre versiones.
    sudo dnf system-upgrade download --releasever=44
    sudo dnf system-upgrade reboot

Si lo hacés desde una versión nueva, me refiero a una versión con soporte, el upgrade no es necesario, diría yo que con update alcanza.

Una vez actualizada la pc, hay que instalarle SSH para que podamos administrarla desde otro sitio.

    bash
    sudo dnf install openssh-server
    sudo systemctl enable --now sshd
    sudo firewall-cmd --add-service=ssh --permanent
    sudo firewall-cmd --reload

Con esto instalamos SSH y le indicamos al firewall que habilite los puertos así como que haga permanente la cosa. A partir de este momento podés hacer todo desde la PC principal mientras Jelly esté encendida.

## Ahora sí, a trabajar para nuestro server media.

Nos conectamos a Jelly:

    bash
    ssh usuario@ip-de-jelly

## Instalamos Podman

    bash
    sudo dnf install podman 

El estándar de Linux para aplicaciones indica que debe instalarse en /opt ya que es software que no viene con el sistema operativo de base, es decir, ¿software de terceros? a /opt.
Podría haberlo instalado en cualquier lado, ojo, como '/Documentos'... pero vamos a seguir las buenas prácticas, así que ahí lo hacemos.

    bash
    sudo mkdir -p /opt/jellyfin/{config,cache,media}
    sudo chown -R $USER:$USER /opt/jellyfin

>Si tu usuario se llama *pepito*, $USER se reemplaza automáticamente por *pepito*.

Si vas a usar un disco externo tenés que montarlo y apuntar la carpeta *media* ahí.

Tuve un problema con SELinux, otra vez, que me denegaba el acceso al path de /config/log.

    bash
    Access to the path '/config/log' is denied

Se soluciona así, etiquetando el contenedor para que SELinux entienda que es seguro.

    sudo dnf install policycoreutils-python-utils
    sudo semanage fcontext -a -t container_file_t "/opt/jellyfin(/.*)?"
    sudo restorecon -Rv /opt/jellyfin

## Ejecutar Jellyfin con Podman

Usé la imagen de linuxserver/jellyfin porque por alguna razón que todavía desconozco maneja mejor los permisos con variables PUID / PGID que la versión oficial de Jellyfin.

    bash
    podman run -d \
    --name jellyfin \
    -p 8096:8096 \
    -v /opt/jellyfin/config:/config \
    -v /opt/jellyfin/cache:/cache \
    -v /opt/jellyfin/media:/media:ro \
    -e PUID=1000 \
    -e PGID=1000 \
    -e TZ=America/Argentina/Buenos_Aires \
    --restart unless-stopped \
    docker.io/linuxserver/jellyfin

Acá vas a tener que reemplazar el PUID=1000 por el que sea tuyo, el id -u y el id -g.

## Probar Jellyfin

Desde el navegador remoto digamos:

```http
http://ip-de-jelly:8096
```

Configuré el usuario administrador, agregué una biblioteca apuntando a /media y listo.

<img src="/blog/img/Bienvenida.png" alt="Bienvenida Jelly" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

Hay que cargar la biblioteca, luego escanear, cuestiones menores después de todo lo que hicimos.

<img src="/blog/img/Conf_Biblioteca.png" alt="Configuración Biblioteca Jelly" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

## Las últimas vueltas de tuerca
Parecía que todo andaba, pero igual hubo algunas cuestiones de permisos y de acceso.
- **Permisos dentro del contenedor**: Aunque en el host los archivos eran míos, Jellyfin los veía como `root`. La solución fue forzar el cambio de propietario dentro del contenedor con `chown` (y un par de recreaciones del contenedor con los permisos adecuados).
- **Los archivos en `exfat` no soportaban etiquetas SELinux**: Terminé formateando el disco externo en el que tengo las series a `ext4` para que todo fuera más limpio y seguro.

## ¿Cómo rinde?

Si tu tele o dispositivo no soporta el formato original (ej: 4K H.265 en una TV vieja), Jellyfin **convierte el video sobre la marcha**. Eso sí, el CPU se esfuerza:

|Archivo|Calidad|CPU(idle/transcoding)|RAM|
|-------|-------|---------------------|---|
|1080 P| H.264 | ~5-10%|~800 MB|
|4K (transcoding)| H.265 | ~40-60% | 1.2 GB|

El i7 que tengo aguanta bien 2-3 streams simultáneos (más que suficiente para mi gato y yo)


## ¿Qué aprendimo?

* Ya lo sabíamos pero es fundamental actualizar el SO (especialmente si estuvo el equipo apagado un tiempo juntando mugre)
* SELinux no es un enemigo pero tiene sus mañas, solo hay que aprender a domesticarlo.
* Podman rootless es un gran amigo, también podés dedicarle un usuario extra a todo esto, cambios mínimos.
* La imagen de linuxserver/jellyfin es mucho más amigable con Podman y SELinux que la oficial.


## ¿Qué sigue?

Usarlo, cargarle series y ver cómo se desenvuelve.

Bueno, se ve algo así la previsualización de los capítulos, tiene modo fullscreen y demás opciones clásicas de cualquier plataforma de streaming.
Hay aplicaciones Jellyfin para SmartTV y para Android.

<img src="/blog/img/Eternauta.png" alt="Eternauta" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

Y a disfrutar, *lo nuevo funciona, Juan.*