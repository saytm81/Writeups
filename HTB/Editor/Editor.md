# Writeup — HackTheBox: **Editor**

**Target:** `editor.htb` (10.10.11.80)
**Autor:** *Say*
**Fecha:** 2025-09-18


## Resumen

Realicé un reconocimiento y enumeración sobre `editor.htb`, descubrí una instancia de XWiki vulnerable (versión Debian 15.10.8) con una vulnerabilidad RCE reportada como **CVE-2025-24893** y obtuve una shell con privilegios del usuario `xwiki`. A partir de ahí localicé credenciales en la configuración (`hibernate.cfg.xml`) que permitieron el acceso por SSH como `oliver`. Posteriormente identifiqué un binario SUID de Netdata que permitía escalada a root (vinculado a **CVE-2024-32019** en el contexto del reto). En `/root` encontré la `root.txt`.

> Nota: todas las acciones fueron realizadas en el entorno controlado del CTF.

---

## 1 — Reconocimiento inicial

### Comprobación de alcance (ping)

```bash
ping -c3 10.10.11.80
```

### Escaneo de puertos (descubrimiento rápido)

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 10.10.11.80
```

**Puertos abiertos identificados**

* `22/tcp`  — SSH
* `80/tcp`  — HTTP (nginx)
* `8080/tcp` — HTTP (servicio adicional / proxy)

### Detección de versiones (servicios relevantes)

```bash
nmap -p22,80,8080 -sCV 10.10.11.80
```

Resultados relevantes:

* `OpenSSH 9.6p1` (22/tcp)
* `nginx 1.24.0` (80/tcp)
* Servicio HTTP en puerto `8080` que presentó cabeceras/elementos de una instancia XWiki.

---

## 2 — Enumeración web

### Ajuste de hosts

Para resolver virtual hosts añadí:

```
10.10.11.80 editor.htb
```

### Búsqueda de vhosts/subdominios

Se usó fuzzing de vhosts contra la IP apuntando `Host:` a `FUZZ.editor.htb`.
Resultado notable: se descubrió el host `wiki.editor.htb`, donde se encontraba la instancia de XWiki.

### Observaciones en la web

* Página principal mostraba XWiki (pack Debian).
* Se identificó la versión: **XWiki Debian 15.10.8**.

---

## 3 — Vulnerabilidad encontrada: XWiki RCE (CVE-2025-24893)

Durante la búsqueda de información sobre la versión detectada, se identificó la vulnerabilidad **CVE-2025-24893** (RCE en ciertas rutas de la instalación XWiki). Buscando PoC públicos se localizó un repositorio con un exploit pública (PoC) que permite enviar un payload para ejecutar comandos arbitrarios en la aplicación vulnerable.

> **Evidencia**: versión XWiki detectada (15.10.8) + referencia a la vulnerabilidad pública.

**Acción realizada (alto nivel):**

* Se utilizó un PoC público disponible en GitHub para verificar la vulnerabilidad y obtener una shell en la máquina objetivo (entorno CTF).
* Tras la ejecución del PoC se obtuvo acceso con los privilegios del servicio XWiki (usuario de la aplicación).

> En el informe se omiten los detalles operativos / payloads concretos por razones de seguridad; la evidencia se puede aportar al organizador o en auditoría responsable.

---

## 4 — Acceso inicial: enumeración tras la shell

Con la shell del servicio XWiki se realizó una exploración inicial del sistema bajo el usuario de la aplicación:

* Revisión de `/home` detectó un usuario `oliver`.
* Inspeccionando la estructura de la aplicación y sus ficheros de configuración, se localizó el directorio de configuración de XWiki (`/usr/lib/xwiki/WEB-INF`) que contenía `hibernate.cfg.xml`.
* En `hibernate.cfg.xml` se encontraron credenciales de base de datos:

```xml
<property name="hibernate.connection.password">theEd1t0rTeam99</property>
```

Con esas credenciales y el user `oliver` se procedió a intentar autenticación por SSH.

---

## 5 — Escalada a usuario de sistema (`oliver`)

* Acceso SSH como `oliver` (uso de las credenciales encontradas): autenticación exitosa.
* Tras entrar como `oliver` se encontró el fichero `user.txt` en su home — **flag de usuario capturada**.

---

## 6 — Búsqueda de vectores para escalada a root

Se procedió a enumerar SUIDs y binarios con permisos especiales:

```bash
find / -perm -4000 -type f 2>/dev/null
```

Un resultado importante fue:

```
/opt/netdata/usr/libexec/netdata/plugins.d/ndsudo
```

* `ndsudo` estaba presente con permisos `-rwsr-x---` (propietario `root`, grupo `netdata`) → indica bit SUID y ejecución por miembros del grupo `netdata`.
* Investigación adicional mostró que el caso está relacionado con un vector conocido (en el contexto del reto se asoció a CVE-2024-32019 / PoC público).

---

## 7 — Explotación del SUID de Netdata y obtención de root (resumen)

**Acción (alto nivel):**

* Se localizó un PoC público que demuestra la explotación del binario SUID afectado.
* Tras ejecutar y adaptar el PoC en el entorno del CTF, se obtuvo ejecución con privilegios elevados y acceso al directorio raíz del sistema.

**Evidencia resultante:**

* Acceso con UID 0 (root).
* En `/root` se encontró `root.txt` — **flag de root capturada**.

> Nota de seguridad: en este write-up se describen pasos y referencia a PoC públicos sin incluir comandos de explotación sensibles en texto abierto.

---

## 8 — Post-explotación (acciones documentales / observables)

Acciones típicas que se podrían realizar tras obtener acceso root (solo listadas, no ejecutadas en el informe):

* Revisión de configuración y credenciales (backups, `.env`, bases de datos).
* Auditoría de logs y detección de persistencia.
* Reporte responsable de las vulnerabilidades y recomendaciones de mitigación.

---

## 9 — Mitigaciones y recomendaciones

Para mitigar los vectores empleados y reducir la superficie de ataque recomiendo:

**Para XWiki (RCE)**

* Actualizar XWiki a la versión parcheada inmediatamente.
* Restringir el acceso a interfaces administrativas y endpoints sensibles.
* Aplicar WAF / reglas de entrada que bloqueen payloads sospechosos.
* Revisar y proteger ficheros de configuración (`WEB-INF`, `hibernate.cfg.xml`) y evitar almacenar credenciales en texto plano; usar secretos gestionados.

**Para Netdata / SUID**

* Eliminar bits SUID innecesarios: `chmod u-s /ruta/al/binario` si no es imprescindible.
* Revisar pertenencia de grupos (no añadir usuarios no confiables a `netdata`).
* Aplicar control de acceso (AppArmor/SELinux) y limitar las funcionalidades del servicio.
* Mantener software actualizado y aplicar parches conocidos para CVEs.

---

## 10 — Conclusiones y lecciones aprendidas

* La exposición de **instalaciones con versiones sin parchear** (p. ej. XWiki) permite RCE y pivot interno.
* Los ficheros de configuración con credenciales en texto plano incrementan el riesgo de escalada lateral/vertical.
* Binarios SUID mal configurados o con lógica insegura (pertenecientes a servicios) son una fuente frecuente de escalada a root.
* En entornos productivos: aplicar hardening, minimización de privilegios y auditorías periódicas.

---

## Referencias

* CVE-2025-24893 — (referencia pública / advisories)
* Repositorio PoC XWiki (ejemplo): `https://github.com/gunzf0x/CVE-2025-24893`
* CVE-2024-32019 / PoC relacionado con netdata SUID (referencia pública)
* Documentación Netdata, XWiki y guías de hardening

---
