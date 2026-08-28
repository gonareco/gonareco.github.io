---
title: "Kali Linux en Fedora con KVM: virtualización nativa para pentesting"
date: 2026-06-03
tags: ["Kali Linux", "virt-manager", "KVM", "Pentesting", "Ethical Hacking", "Fedora"]
---

## El contexto

Ejecutar herramientas de auditoría de red (Nmap, Metasploit, Burp Suite) sin contaminar el sistema anfitrión ni depender de hardware dedicado.

## La solución

Máquina virtual con virt-manager (KVM). Kali aislado, Fedora limpio, rendimiento óptimo.

## ¿Por qué KVM y no VirtualBox?

En Fedora, KVM + virt-manager es la opción nativa y superior:

- **KVM está en el kernel.** No se cargan módulos externos ni dependencias adicionales.
- **Rendimiento casi nativo.** Hipervisor tipo 1, overhead mínimo. VirtualBox es tipo 2 y corre sobre el SO anfitrión.
- **Integración nativa con el ecosistema Fedora/RHEL.** La misma base que entornos empresariales.
- **Snapshots eficientes.** Instantáneas rápidas, confiables y con soporte directo desde virsh o interfaz gráfica.

## Instalación del entorno
    bash
    sudo dnf install @virtualization
    sudo systemctl enable --now libvirtd
    sudo usermod -aG libvirt $USER

## Configuración de la VM

- Descargar la ISO de Kali desde kali.org.
- Crear nueva VM en virt-manager.
- RAM: 4 GB como mínimo.
- Disco: 40 GB (formato qcow2). Con menos espacio se compromete la actualización del sistema.
- Red: NAT por defecto. Para auditorías específicas se configura red puente.
- Particionado: "Todo en una partición" para evitar tablas MBR/MSDOS con swap intermedia (para una VM esto es suficiente, en un servidor productivo recomendaría particiones específicas para /home, /var, etc. )

## Gestión de instantáneas

Las instantáneas se crean con la VM apagada para garantizar consistencia.

### Crear instantánea base


    bash
    sudo virsh snapshot-create-as Kali "Base" --description "Estado post-instalación"

### Listar instantáneas

    bash
    sudo virsh snapshot-list Kali

### Restaurar

    bash
    sudo virsh snapshot-revert Kali Base

Este flujo permite volver a un estado limpio en segundos ante cualquier inconsistencia o bloqueo por contraseña.

## Uso práctico

* Escaneos de red con Nmap.
* Explotación controlada con Metasploit.
* Auditoría de vulnerabilidades sobre Metasploitable 2 en la misma red.
* Pruebas de herramientas sin impacto en Fedora.

## Ventajas diferenciales

* Aislamiento total: El anfitrión no se ve afectado por configuraciones agresivas de red o paquetes experimentales.
* Rendimiento estable: KVM aprovecha las extensiones de virtualización del hardware sin capas intermedias.
* Recuperación inmediata: Las instantáneas eliminan la necesidad de reinstalar por errores de configuración o credenciales.

## Conclusión

Kali sobre KVM en Fedora es la combinación más limpia, rápida y profesional para tener un entorno de pentesting portable y seguro en tu máquina de uso diario.