---
name: joomla-vineria
description: Plan and validate Joomla adaptation of Vineria del Este without altering the approved designs or live restaurant.
---

# Guía de trabajo: Vinería del Este en Joomla

Este archivo es una guía del repositorio para futuras sesiones, no una extensión instalada en Joomla ni una skill instalada globalmente en ChatGPT.

## Cuándo usarla

Al adaptar, instalar, mantener o desplegar en Joomla el restaurante, su tienda o su gestión. Leer primero `docs/JOOMLA_MIGRACION_ES.md` y consultar de nuevo las fuentes oficiales si cambian las versiones.

## Reglas del proyecto

- Conservar los ocho modelos existentes: v1, v2, v3, v4, v5, v6a, v6b y v08. No crear nuevas variantes sin petición expresa.
- Restaurante y tienda deben compartir estilo en cada modelo. La gestión es común y separada.
- El logotipo original no se redibuja. Guardar los dibujos de platos a color como alternativas; utilizar las versiones de halftone negro en los estilos fanzine. No usar la ilustración de las personas rechazada ni el icono verde con estrella.
- Alemán como idioma principal; español como identidad y nombres de platos.
- Todo cambio funcional de contenido debe alcanzar los ocho modelos, no sólo el último.
- La demo pública guarda contenido localmente. Nunca describir ese almacenamiento como publicación para otros visitantes, autenticación real o gestión de base de datos.

## Puertas de instalación

1. Confirmar Joomla, PHP, base de datos, plantilla, T3 y extensiones en un acceso autorizado. El crédito JoomlArt no identifica el hosting.
2. Copia completa de archivos y base de datos; restauración de prueba antes de escribir en producción.
3. Si se prepara plantilla, usar manifiesto `templateDetails.xml`, archivo `index.php`, posiciones de módulos y assets locales. Validar contra la versión exacta. No copiar una plantilla de una versión incompatible.
4. Instalar mediante el gestor de extensiones; asignar primero a menús de prueba. No usar Quickstart ni sustituir la raíz con un index.html.
5. Joomla controla sesión, permisos, usuarios y contraseñas. No introducir credenciales en el repositorio, HTML o JavaScript.
6. La carta necesita categorías y campos estructurados; noticias necesitan publicar/despublicar, imagen, texto y fechas; tienda necesita un componente de comercio compatible y vistas adaptadas al diseño.
7. Preservar reservas, formularios, mapas, enlaces y redirecciones. Cobros, correo e Instagram permanecen desactivados hasta tener integraciones reales probadas.

## Validación de una entrega

Comprobar carta completa, categorías añadidas/renombradas/eliminadas, productos y precios, visibilidad, noticias con y sin foto, cuatro/ocho fotos de galería sin duplicados, navegación, teclado, móvil y comparador. Distinguir comprobaciones de estructura de pruebas reales de instalación en Joomla. Entregar URL verificada y manifiesto de lo desplegado.

## Fuentes

https://www.joomlart.com/joomla/templates/ja-diner
https://www.joomlart.com/documentation/joomla-templates/ja-diner
https://manual.joomla.org/docs/building-extensions/templates/template-details-file/
https://docs.joomla.org/Help5.x:Extensions:_Install
https://www.hikashop.com/download
