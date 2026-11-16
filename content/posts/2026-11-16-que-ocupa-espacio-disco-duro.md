---
title: "Cómo saber qué ocupa espacio en tu disco duro (y liberarlo)"
description: "Descubre qué está llenando tu disco duro en Windows y Mac con las herramientas del sistema y WinDirStat, y aprende a liberar gigas sin borrar nada importante."
date: 2026-11-16
category: ordenador
emoji: 💾
tags: disco duro, windows, mac, almacenamiento, limpieza
slug: que-ocupa-espacio-disco-duro
---

Para saber qué ocupa espacio en tu disco duro en Windows, ve a **Configuración › Sistema › Almacenamiento**: verás el espacio dividido por categorías (aplicaciones, archivos temporales, documentos, imágenes…). Si necesitas ver carpeta por carpeta qué es lo más pesado, usa un programa gratuito como **WinDirStat**, que lo muestra en un mapa visual.

Te explicamos cómo hacerlo en Windows y en Mac, y qué puedes borrar sin miedo.

## En Windows

### 1. Configuración de almacenamiento

1. Abre **Configuración** (Windows + I).
2. Ve a **Sistema › Almacenamiento**.
3. Verás las categorías ordenadas por tamaño. Pulsa **Mostrar más categorías** para verlas todas.
4. Entra en cada una para ver el detalle y borrar lo que no necesites.

Las categorías que más suelen ocupar son **Aplicaciones instaladas**, **Archivos temporales** y **Otros**.

### 2. Ver el tamaño de carpetas en el Explorador

Abre el **Explorador de archivos**, haz clic derecho en una carpeta (por ejemplo, **Descargas** o **Vídeos**) y elige **Propiedades**. Verás cuánto ocupa. Es un método lento si quieres revisar muchas carpetas, pero no necesitas instalar nada.

### 3. WinDirStat o WizTree: el mapa visual

Estos programas gratuitos analizan todo el disco y muestran cada archivo como un rectángulo de color: cuanto más grande, más espacio ocupa. En un minuto descubres ese vídeo de 20 GB olvidado o la carpeta de un juego que ya no usas.

1. Descarga **WinDirStat** o **WizTree** desde su web oficial.
2. Ábrelo y elige la unidad **C:**.
3. Espera a que termine el análisis y haz clic en los rectángulos más grandes para ver qué son.

WizTree es especialmente rápido en discos grandes.

## En Mac

1. Abre el menú Apple › **Ajustes del Sistema › General › Almacenamiento**.
2. Verás una barra con el espacio por categorías y una lista de recomendaciones.
3. Pulsa el icono **(i)** junto a cada categoría para ver los archivos y borrarlos.

Para ver archivos grandes en cualquier carpeta, abre el **Finder**, pulsa **Cmd + F**, elige **Tamaño de archivo › es mayor que** y escribe, por ejemplo, 1 GB.

## Qué suele ocupar más espacio

| Culpable | Dónde mirar | ¿Se puede borrar? |
|---|---|---|
| Descargas antiguas | Carpeta Descargas | Sí, revisa antes |
| Archivos temporales | Configuración › Almacenamiento | Sí |
| Papelera de reciclaje | Escritorio | Sí, vacíala |
| Juegos y programas | Aplicaciones instaladas | Sí, si no los usas |
| Vídeos y fotos | Carpetas Vídeos e Imágenes | Mejor pásalos a un disco externo |
| Copias de seguridad del móvil | Carpeta de iTunes o Apple Devices | Sí, las antiguas |
| Windows.old | Archivos temporales | Sí, tras 10 días de actualizar Windows |
| Archivo de hibernación | Raíz de C: | Solo con cuidado (ver más abajo) |

## Cómo liberar espacio sin riesgo

1. **Vacía la papelera.** Parece obvio, pero a veces acumula varios gigas.
2. **Borra los archivos temporales:** Configuración › Sistema › Almacenamiento › **Archivos temporales**. Desmarca **Descargas** si no quieres borrarla y pulsa **Quitar archivos**.
3. **Activa el Sensor de almacenamiento** para que Windows limpie automáticamente la papelera y los temporales.
4. **Desinstala programas que no uses:** Configuración › Aplicaciones › Aplicaciones instaladas, ordena por tamaño.
5. **Mueve fotos y vídeos** a un disco externo o a la nube (OneDrive, Google Drive). [[amazon:disco duro externo 2tb|Ver discos externos en Amazon]]
6. **Usa los archivos a petición de OneDrive:** los archivos siguen visibles pero solo se descargan cuando los abres.

## Consejo: el espacio que conviene dejar libre

Intenta mantener al menos un **15-20 % del disco libre**. Windows necesita espacio para actualizaciones, archivos temporales y la memoria virtual. Con el disco casi lleno, el ordenador va más lento y las actualizaciones pueden fallar.

## Error común que debes evitar

Borrar carpetas del sistema que no conoces porque «ocupan mucho», como **Windows**, **WinSxS**, **Program Files** o **System32**. Puedes dejar el ordenador sin arrancar. Si un archivo o carpeta forma parte de Windows, deja que sea el propio sistema quien lo limpie con las herramientas de Almacenamiento.

## Preguntas frecuentes

### ¿Qué es la categoría «Otros» y por qué ocupa tanto?
Incluye archivos que Windows no sabe clasificar: carpetas grandes de programas, máquinas virtuales o archivos sueltos. Usa WinDirStat para ver qué contiene exactamente.

### ¿Puedo borrar la carpeta Windows.old?
Sí, si tu ordenador funciona bien después de una gran actualización. Se borra desde Archivos temporales, marcando **Instalaciones anteriores de Windows**. Después ya no podrás volver a la versión anterior.

### ¿Y el archivo hiberfil.sys?
Es el archivo de hibernación y puede ocupar varios gigas. Puedes desactivar la hibernación si no la usas, pero en portátiles conviene dejarla activa.

### ¿Cada cuánto debo limpiar el disco?
Con el Sensor de almacenamiento activado, apenas tendrás que hacerlo. Una revisión manual cada pocos meses es suficiente.
