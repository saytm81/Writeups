1. Comprobación de Conectividad

ping 10.10.11.55

2. Escaneo de Puertos Abiertos

nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 10.10.11.55

✅ Puertos abiertos detectados:

    22/tcp → SSH
    80/tcp → HTTP

3. Detección de Versiones de Servicios

nmap -p22,80 -sCV 10.10.11.55

Resultados:

    22/tcp → OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
    80/tcp → Apache httpd 2.4.52
