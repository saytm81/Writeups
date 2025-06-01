# Análisis de vulnerabilidad XSS y SSTI en aplicación web

## 1. Redirección inicial

Al iniciar la aplicación, se realiza una redirección automática a una página web donde se presenta un campo de entrada (`input`) para el usuario.

## 2. Prueba de inyección XSS

Se probó una inyección básica de tipo XSS utilizando el siguiente payload:

```html
<script>alert('XSS')</script>
```

Este intento no generó una alerta, lo que indica que probablemente haya mecanismos de sanitización en el front-end o back-end.

## 3. Inspección del backend

Al revisar los archivos de la aplicación, se identificó el archivo `main.py`, en el cual se observó el uso del motor de plantillas **Mako**.

## 4. Búsqueda de vulnerabilidades en motores de plantillas

Dado que Mako es un motor de plantillas, se investigaron posibles vulnerabilidades relacionadas con **Server-Side Template Injection (SSTI)**. Se utilizó como referencia el siguiente repositorio:

🔗 [PayloadsAllTheThings - SSTI en Python](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Python.md)

## 5. Explotación exitosa y obtención de la flag

Se logró explotar la vulnerabilidad SSTI con el siguiente payload de Mako:

```mako
${self.module.cache.util.os.popen('cat /flag.txt').read()}
```

Este comando permitió leer el contenido del archivo `flag.txt`, confirmando la existencia de una vulnerabilidad de inyección de plantillas del lado del servidor.

---
