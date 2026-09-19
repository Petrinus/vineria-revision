# Vinería del Este — traslado del catálogo existente a OpenAI Sites

## Estado real — 19 de septiembre de 2026

Migración solicitada por Pedro. NO desplegada en Sites desde la conversación que prepara este documento: esa sesión permite leer y escribir en GitHub, pero no dispone de la herramienta de creación/publicación de Sites. Este archivo documenta el traspaso; no es una configuración de hosting ni demuestra una publicación.

Repositorio de origen: `Petrinus/vineria-revision`, rama `main`.
Revisión observada antes de añadir este documento: `2efda4999a35b6531ec2beb942e7d4bb29f2f3a4`.
Antes de empezar, leer de nuevo la rama actual y conservar cualquier edición posterior; no restablecerla a esta revisión.

## Encargo autorizado

Trasladar TODO el catálogo actual a UN Site de revisión público, visitable sin cuenta ni contraseña. Primero migrar y comprobar la fidelidad. Después se harán los cambios que Pedro indique en cada diseño y página. No crear una novena propuesta, rehacer las páginas, seleccionar un diseño ganador ni sustituir la web comercial real. Mantener GitHub y las publicaciones anteriores intactos como respaldo.

## Origen comprobado

La portada `site/index.html` contiene el selector y comparador de estas ocho parejas:

| Identificador | Restaurante | Tienda |
| --- | --- | --- |
| v1 | site/entwuerfe/v1/index.html | site/entwuerfe/v1/shop/index.html |
| v2 | site/entwuerfe/v2/index.html | site/entwuerfe/v2/shop/index.html |
| v3 | site/entwuerfe/v3/index.html | site/entwuerfe/v3/shop/index.html |
| v4 | site/entwuerfe/v4/index.html | site/entwuerfe/v4/shop/index.html |
| v5 | site/entwuerfe/v5/index.html | site/entwuerfe/v5/shop/index.html |
| v6a | site/entwuerfe/v6a/index.html | site/entwuerfe/v6a/shop/index.html |
| v6b | site/entwuerfe/v6b/index.html | site/entwuerfe/v6b/shop/index.html |
| v08 | site/entwuerfe/v08/index.html | site/entwuerfe/v08/shop/index.html |

Gestión común y separada: `site/verwaltung/index.html` y `site/verwaltung/vorschau.html`. La vista previa carga `site/assets/management-preview.js`.

Estos son puntos de entrada, no una lista completa de archivos. Importar todos los recursos de `site/` y seguir sus dependencias: páginas interiores, fichas, carrito, checkout de prueba, CSS, JavaScript, imágenes, miniaturas, datos y enlaces legales/reservas. Conservar también los directorios de fuente existentes (`shared/`, `src/`, `models/`, `proposal-source/`, `tools/`, `server/`) como código, sin publicarlos indiscriminadamente como recursos web.

No regenerar los estilos con antiguos scripts sin comprobar primero que no sobrescriban correcciones posteriores. Mantener la identidad de cada pareja y especialmente la composición collage de v08. No reintroducir el icono verde con estrella ni sustituir fotografías por imágenes inventadas.

## Gestión y datos: no confundir traslado con integración

La página de gestión comprobada se describe expresamente como demostración pública: no tiene servidor protegido conectado, no recibe contraseñas reales y guarda modificaciones solo en el navegador. El selector de categorías de su HTML tiene cuatro opciones fijas. Las mejoras solicitadas de categorías editables, borrado de filas y gestión de fotos deben comprobarse en el código actual; no presentarlas como hechas por el mero hecho de migrar.

Los datos guardados en el navegador del dominio anterior no están necesariamente en GitHub y no deben darse por transferidos al nuevo dominio. Preservar los datos locales si se tiene acceso a ellos; no borrar ni restablecer el origen. No fingir que una copia del HTML proporciona guardado compartido. Una futura gestión operativa exige persistencia y autorización reales, aparte de la demostración pública.

Mantener desactivados cobros y pedidos reales. No activar Instagram automático ni envío de formularios como si estuvieran conectados. Conservar su comportamiento actual y sus advertencias. No publicar secretos, credenciales, datos personales de clientes ni archivos privados del servidor.

## Ejecución en una sesión con Sites

1. Abrir el proyecto actual y comprobar su compatibilidad con el runtime y formato de despliegue vigentes de Sites. Aplicar únicamente adaptaciones técnicas necesarias para servirlo, sin rediseñarlo.
2. Utilizar `site/index.html` como entrada del catálogo. Preferir servir `site/` como raíz pública manteniendo las rutas relativas. Comprobar rutas anidadas, archivos `.html`, parámetros de consulta y recursos externos.
3. Verificar los ocho restaurantes y ocho tiendas, sus páginas interiores y el comparador en escritorio y móvil. Comprobar las dos entradas de gestión sin activar una administración pública real.
4. Publicar UN Site con acceso público y sin inicio de sesión para visitantes, tal como ya autorizó Pedro. No cambiar DNS ni sustituir la web comercial.
5. Abrir la URL publicada como visitante sin sesión. Validar navegación, recursos y separación de gestión. Entregar esa URL solo después de verificarla.

Documentación oficial consultada: https://learn.chatgpt.com/docs/sites . El flujo de creación/publicación está en ChatGPT web o escritorio. Este documento no presupone un comando CLI ni inventa una configuración de `.openai/hosting.json`.

## Definición de completado

Existe una URL real de Sites que abre el selector para visitantes sin sesión; están las ocho parejas y sus recursos; la gestión continúa separada; las pruebas anteriores están registradas; GitHub y los diseños de origen se conservan. Un archivo, commit, ZIP o despliegue de GitHub NO equivale a una migración a Sites.
