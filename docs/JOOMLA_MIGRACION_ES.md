# Vinería del Este: adaptación a Joomla

Revisión: 19 de septiembre de 2026. Este documento es un plan de instalación, no una confirmación de que la web nueva esté instalada en el servidor del restaurante.

## Qué sabemos y qué no

Joomla es el gestor de contenidos. JoomlArt es el proveedor de plantillas y extensiones, no el alojamiento identificado por el enlace del pie. La web pública incluye recursos bajo `templates/ja_diner/`, y el crédito de su pie coincide con el documentado por JoomlArt para JA Diner, basada en T3. El proveedor de alojamiento, la versión exacta de Joomla, la versión de PHP, las extensiones instaladas y la licencia de JA Diner siguen sin confirmarse. No hay que deducirlos del copyright del pie.

La ficha actual de JA Diner declara Joomla 4 y 5. Parte de su manual todavía habla de Joomla 3 y requisitos PHP antiguos: sirve para comprender la estructura, pero no para elegir versiones seguras ni confirmar compatibilidad con Joomla 6.

## Qué contiene GitHub ahora

Ocho alternativas de diseño con restaurante y tienda, un comparador y una demostración de gestión. Son páginas HTML/CSS/JS. La tienda es de prueba, sin cobros. Los cambios de la gestión pública que usan localStorage sólo afectan al navegador que los hace: no son una base de datos compartida ni la gestión definitiva de Joomla.

No se debe subir el ZIP entero al instalador de Joomla esperando una conversión automática. No se debe poner el `index.html` del comparador en la raíz del restaurante: podría ocultar el `index.php` de Joomla. No sustituir `configuration.php`, `.htaccess`, la base de datos ni el núcleo del CMS.

## Plan recomendado para este proyecto

1. Inventariar en `/administrator`: versión de Joomla y PHP, plantilla activa, T3, módulos JA ACM, menús, alias, redirecciones, reserva Tebi y extensiones. No guardar contraseñas, tokens ni configuración privada en GitHub.
2. Obtener una copia completa de archivos y base de datos, y comprobar su restauración en un subdominio de pruebas no indexable. No probar cambios sobre el restaurante publicado.
3. Mantener los ocho estilos para comparar; convertir la opción elegida, o las que se quieran probar dentro de Joomla, en estilos de una plantilla propia `tpl_vineria`. Crear un paquete instalable con `templateDetails.xml`, `index.php`, CSS/JS, medios y posiciones de módulos. No cambiar el diseño porque el CMS sea Joomla.
4. Usar la autenticación, sesiones y permisos de Joomla para la gestión. No incrustar usuarios ni contraseñas en HTML o JavaScript. Los accesos Buñol y Kraft se crearán en el CMS con contraseña personal y permisos mínimos; el código provisional no se publicará.
5. Carta: categorías editables y entradas con nombre, descripción y precio como campos estructurados; publicar/despublicar para ocultar y papelera para eliminar con posibilidad de recuperación. Los nombres de las pestañas deben derivarse de las categorías, no estar fijados en el código.
6. Noticias: artículos de una categoría propia, imagen, título, texto, enlace opcional y fechas de publicación. Un módulo de portada muestra una o dos entradas publicadas; despublicar el módulo oculta el bloque entero.
7. Tienda: comprobar primero si existe un componente de comercio instalado. Si no, evaluar HikaShop como opción Joomla; su documentación incluye productos, imágenes, precios, envíos y plugins de pago. No instalar, contratar o activar cobros sin configurar previamente cuenta comercial, impuestos, correo, edad, disponibilidad y políticas. Adaptar sus vistas mediante overrides al mismo estilo del restaurante.
8. Eventos y catering: formulario respaldado por Joomla/servidor, validación, protección CSRF, antispam y correo SMTP probado. El formulario `mailto:` de la revisión no equivale a entrega automática.
9. Instagram: módulo activable de cuatro u ocho fotos con autorización oficial de la cuenta, caché de imágenes y renovación de autorización en servidor. No pedir el password de Instagram en la web ni exponer tokens en el navegador. Mientras no esté conectado, identificar la galería de ejemplo como tal.
10. Preservar dominios, alias, vínculos y redirecciones. Asignar la plantilla primero sólo a los menús de pruebas. Revisar móvil, navegación, accesibilidad, imágenes, reservas, formularios, pedidos de prueba y restauración. Cambiar la plantilla de producción sólo después de validar la copia.

## Cómo se instala una plantilla propia

En Joomla 4/5: **Sistema → Instalar → Extensiones → Subir archivo del paquete**. Se sube el ZIP específico de la plantilla, con su manifiesto en la raíz. Después: **Sistema → Plantillas del sitio / Estilos**; crear o seleccionar el estilo y asignarlo únicamente al menú de pruebas. Las denominaciones pueden variar según idioma y versión.

La vía alternativa documentada es copiar los archivos de una extensión a su carpeta correcta y usar **Sistema → Instalar → Descubrir**; no hace falta recurrir a ella cuando funciona el instalador normal.

**No usar el paquete Quickstart de JoomlArt sobre la web existente.** Quickstart reproduce su demo e incluye una instalación completa; no es nuestro diseño nuevo ni una actualización segura del sitio actual.

## Fuentes oficiales consultadas

- Web existente: https://vineriaytapas.de/
- JA Diner, ficha de compatibilidad: https://www.joomlart.com/joomla/templates/ja-diner
- JA Diner: estructura, T3, instalación manual, módulos y crédito del pie: https://www.joomlart.com/documentation/joomla-templates/ja-diner
- Manifiesto de plantillas Joomla: https://manual.joomla.org/docs/building-extensions/templates/template-details-file/
- Instalador Joomla 5: https://docs.joomla.org/Help5.x:Extensions:_Install
- Descubrir extensiones: https://docs.joomla.org/Help5.x:Extensions:_Discover
- Opciones de layouts de módulos y overrides: https://manual.joomla.org/docs/5.4/general-concepts/forms-fields/standard-fields/modulelayout/
- HikaShop, compatibilidad y funciones: https://www.hikashop.com/download
- HikaShop, instalación: https://www.hikashop.com/support/documentation/59-hikashop-how-to-install.html

## Pendientes antes de fabricar el paquete definitivo

Versión exacta de Joomla/PHP; acceso autorizado al administrador o copia completa del sitio; proveedor de alojamiento y entorno de pruebas; compatibilidad de T3/JA Diner y de las extensiones; decisión sobre el componente de tienda. No se ha instalado ni cambiado nada en el alojamiento real.
