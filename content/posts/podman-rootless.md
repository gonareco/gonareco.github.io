---
title: "Podman rootless en Fedora: por qué es más seguro que Docker"
date: 2026-05-08T10:00:00-03:00
draft: false
tags: ["Podman", "Fedora", "Docker", "SELinux", "Seguridad"]
---

## Por qué me cambié a Podman

Sencillamente para probar algo nuevo. Vengo usando Docker desde hace años, como sucede muchas veces un interés inicial se convierte en norma de uso general y luego uno no se vuelve a preguntar por qué usa tal o cual cosa. En definitiva cuando empecé a profundizar en administración de Linux, descubrí que Podman es el estándar en el mundo Red Hat/Fedora. No solo viene en los repositorios oficiales (mientras que Docker requiere agregar un repo externo), sino que tiene una ventaja de seguridad enorme: es rootless por defecto.

## El problema de seguridad con Docker

Docker corre un daemon como root. Eso significa que si un contenedor se ve comprometido, el atacante podría potencialmente escalar privilegios a todo el host. Son riesgos reales no teóricos, ya pasó.

## Rootless = Seguridad por defecto

Con Podman, cada contenedor corre con los permisos de mi usuario. No hay un daemon con privilegios de root corriendo de fondo. Los contenedores se ejecutan como procesos hijos de mi sesión de usuario. Si un contenedor es vulnerable, el daño queda limitado a mis propios archivos.

## SELinux y el flag :Z

El error más común al empezar con Podman en Fedora es este:

    bash
    Permission denied a config.yml


¿El motivo? SELinux. Fedora tiene SELinux activado por defecto, y bloquea el acceso de un contenedor a archivos del host a menos que se lo permitas explícitamente.

La solución es agregar :Z al volumen:


    bash
    podman run -d --name mi-app -v /ruta/absoluta:/ruta/contenedor:Z imagen


La :Z le dice a SELinux que etiquete ese volumen para que el contenedor pueda acceder.
Podman-compose funciona con docker-compose.yml

Otra ventaja: Podman entiende el mismo formato docker-compose.yml. Solo cambiás docker-compose por podman-compose.
Conclusión

Podman Es una mejora real en seguridad, especialmente en entornos Red Hat/Fedora. Si estás en Fedora o RHEL, usá Podman (Podman no me paga nada). Te vas a acostumbrar rápido y tu sistema va a ser más seguro.

Luego hablaremos de SELinux (es tema para un post completo).
