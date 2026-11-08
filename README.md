# Proyecto 2 - Agenda de Contactos

Laboratorio 2 - Manejo e implementacion de Archivos.

Agenda de contactos en Python (Tkinter) guardada en un archivo de registros de tamaño fijo con acceso aleatorio.

## Ejecutar

Requiere Python 3 y reportlab (`pip install reportlab`) para el reporte PDF.

```
python main.py
```

Para comparar la busqueda con indice contra la secuencial:

```
python comparar_busqueda.py
```

## Estructura

```
main.py                     carga la configuracion y abre la ventana
comparar_busqueda.py        mide la busqueda con indice contra la secuencial
contactos/registro.py       campos, largos en bytes y conversion a texto
contactos/archivo.py        lectura y escritura en contactos.dat con seek y tell
contactos/indice.py         indice id -> numero de registro
contactos/herramientas.py   hash sha-256, respaldo zip y metadatos
contactos/exportar.py       exportacion a json y reporte pdf
config/                     configuracion de la app, reutilizada del laboratorio 1
ui/                         ventana principal, menu, contactos, informacion y settings
data/                       contactos.dat, indice.json, contactos.sha256 y respaldos
docs/capturas/              capturas de la app
```

## El registro

| Campo | Bytes |
|---|---|
| id | 5 |
| nombre | 35 |
| telefono | 15 |
| correo | 40 |
| ciudad | 24 |
| salto de linea | 1 |
| **total** | **120** |

Los largos son en bytes y no en caracteres porque el archivo se guarda en UTF-8, donde una ñ ocupa dos bytes. Si se rellenara por caracteres los registros no medirian lo mismo y `seek(numero * 120)` caeria en el lugar equivocado.

El archivo se abre en modo binario y cada contacto se ubica con `seek()`, sin recorrer el resto. Al modificar solo se reescriben esos 120 bytes.

## Eliminar un contacto

El borrado es logico: el id del registro se marca con `*****` y su entrada se quita del indice, asi que deja de aparecer en las busquedas y en las exportaciones. Fisicamente los 120 bytes siguen en el archivo, que no cambia de tamaño. Borrarlo de verdad obligaria a correr todos los registros siguientes y a recalcular el indice completo. El espacio marcado se reutiliza cuando se agrega otro contacto.

## Integridad

Despues de cada cambio se guarda el SHA-256 del archivo en `contactos.sha256`. Al iniciar se vuelve a calcular y se compara, de modo que se detecta cualquier edicion hecha fuera de la aplicacion.
