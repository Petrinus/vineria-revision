# Vinería del Este — restaurante, tienda y gestión

## Lo que está publicado para revisar

El sitio estático está en `site/`. Incluye la portada del restaurante, una home propia de tienda, once fichas de producto, carrito y checkout de prueba, textos de servicio en borrador y dos estilos emparejados. La alternativa fanzine y la editorial conservan restaurante y tienda con el mismo diseño. Todas las páginas de esta publicación llevan `noindex`.

Entrada de revisión temporal:
https://raw.githack.com/Petrinus/vineria-revision/main/site/index.html

Selector de ambas propuestas:
https://raw.githack.com/Petrinus/vineria-revision/main/site/entwuerfe/index.html

El proveedor externo puede mostrar **Open the page** la primera vez. No requiere cuenta de GitHub. Este enlace es público, no privado ni de GitHub Pages. La cuenta de integración no ha obtenido permiso de administración para activar Pages por primera vez. La compilación pública funciona independientemente de esa activación.

## La gestión no se ejecuta en el visor estático

`server/` contiene una gestión PHP real, separada de la vista pública. No es una contraseña escondida en JavaScript. Hay formularios de carta, precios, productos, visibilidad, usuarios, cambio de contraseña, borradores, historial y publicación conjunta de ambos estilos.

El instalador provisiona dos cuentas de administrador, **Buñol** y **Kraft**. La clave inicial se suministra de forma privada durante la instalación y no está incluida en el repositorio. Ambas cuentas deben cambiarla en el primer acceso. Los cambios posteriores requieren una contraseña individual de al menos doce caracteres.

No se han instalado esas cuentas en un servidor público mediante GitHub: las pruebas se ejecutan en una instalación temporal y se elimina su estado al terminar. No introducir la clave real en la vista pública de GitHub/CDN.

## Instalación en el alojamiento controlado por el negocio

Requisitos: PHP 8.2 o superior, sesiones PHP, Python 3.10 o superior con Pillow, HTTPS y acceso de escritura del usuario del servidor a `site/` y al directorio privado. Esta variante utiliza PHP más un generador estático para que los cambios publicados aparezcan en HTML, no solo tras ejecutar JavaScript. No requiere Node ni Excel.

Mantener estas carpetas hermanas:

```
proyecto/
  site/       <- única raíz pública del dominio
  server/     <- NO pública
  tools/      <- NO pública
  src/        <- NO pública
  private/    <- NO pública, permisos 0700
```

En un terminal seguro del alojamiento, no en GitHub Actions ni en el navegador, establecer `VDE_INITIAL_PASSWORD` con la clave inicial acordada y ejecutar `php server/setup.php`. El script no imprime la clave y almacena hashes individuales. Se niega a sobrescribir una instalación existente. Eliminar después esa variable del entorno. No escribir la clave en un archivo público ni pegarla en una incidencia de GitHub.

Configurar `VDE_ORIGIN=https://vineriaytapas.de` para comprobar el origen de los formularios. `VDE_PRIVATE_DIR` permite ubicar el estado fuera del proyecto; `VDE_PYTHON` selecciona el ejecutable Python. No activar `VDE_LOCAL_TEST` en producción: se usa exclusivamente para probar HTTP en localhost.

El instalador añade el acceso PHP en `site/verwaltung/index.php` y una regla de Apache para que `/verwaltung/index.html` también lo abra. En Nginx debe configurarse la equivalencia por el administrador del alojamiento. Denegar acceso por HTTP a archivos de configuración, almacenamiento y código de `server/` aunque exista una configuración accidental del dominio. Hacer copia previa del Joomla, medios y reglas de redirección antes de sustituirlo.

La publicación desde gestión genera primero las páginas en un directorio temporal, luego sustituye archivos mediante renombrado. Modifica restaurante, ambas variantes de tienda y fichas. Los formularios no activan cobros: el checkout de esta entrega permanece en modo demostración. Para venta real faltan proveedor de pago, confirmaciones, datos legales, fiscalidad, stock operativo, etiquetado, verificación de edad y transporte real.

## Qué se ha probado

`python3 tools/qa.py`: enlaces internos, imágenes, tamaños de 320/390/1440 px, carta sin JavaScript, pestañas con teclado, pase de imágenes y pausa, categorías, búsqueda, botella/caja, costes de muestra, recogida de refrigerados, carrito vacío y checkout sin pago.

`python3 server/test.py`: instalación aislada, cuentas iniciales, hashes, cookies HttpOnly, sesión, CSRF, origen, cambio de clave obligatorio, edición sin publicar, control de versiones, alta de productos y páginas propias, publicación de ambos estilos, escape de HTML, historial, cuentas de equipo, cierre de sesión y separación de permisos.

Son pruebas funcionales automatizadas; no equivalen a una auditoría de seguridad ni a una validación jurídica. Los informes y capturas se guardan en los artefactos de GitHub Actions y en el directorio de informes de cada ejecución.

## Dominio y buscadores

Estructura prevista: `/` para el restaurante, `/shop/` para la tienda y `/shop/producto/` para cada ficha. El panel queda en `/verwaltung/`. Los enlaces entre secciones son relativos y permanecen en el mismo dominio.

Las fichas ya son páginas HTML individuales con títulos, descripción y navegación. La revisión no debe aparecer como una tienda que vende productos de ejemplo: conservar `noindex` durante las pruebas. Al publicar el negocio real, confirmar contenidos y precios, elegir una sola variante canónica, ajustar URLs limpias, títulos, canonical, sitemap, robots y redirecciones. No dar por inventariados alias desconocidos del Joomla.

## Imágenes y créditos

Los retratos, terraza y bar provienen del archivo aportado por el cliente. La fotocollage se ha generado a partir de sus referencias y no representa un momento documental fotografiado. El plato de garbanzos procede de la web existente. Los originales y los recursos gráficos se distinguen en los manifiestos de `site/assets/`. Los archivos de referencias ajenas y el vídeo no se publican como contenido del restaurante.

La web existente presenta la marca como texto (`logo-text`); no se ha inventado una imagen de logotipo descargada. Las imágenes de los productos de tienda son ilustraciones o marcadores gráficos, no fotografías de envases confirmados.
