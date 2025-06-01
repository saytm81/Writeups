### Análisis del ejecutable encontrado

Dentro del archivo se identificó un ejecutable llamado `pass`.

Se utilizó la herramienta `strings` para analizar el binario y extraer posibles cadenas de texto legibles. Entre las cadenas encontradas, se identificó una que destaca como posible contraseña:

```
s3cr3t_p455_f0r_gh05t5_4nd_gh0ul5
```

Al ejecutar el programa, este solicita una contraseña. Al ingresar la cadena obtenida previamente, el programa la acepta correctamente y se obtiene la **flag**.
