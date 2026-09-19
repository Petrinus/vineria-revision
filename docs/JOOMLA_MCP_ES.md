# Posible conexión directa con Joomla mediante MCP

Investigación: 19/09/2026. Fuente oficial de JoomlArt: https://www.joomlart.com/joomla-mcp

JoomlArt publica una guía de Joomla MCP que describe gestionar contenido de Joomla desde asistentes compatibles con MCP. El proveedor declara compatibilidad con Joomla 4, 5 y 6 y uso de las funciones API ya incluidas en Joomla. No afirma que Joomla 3 sea compatible.

La guía requiere habilitar los plugins de token y servicios web, un usuario con permisos apropiados y una credencial API revocable. No confundir esa credencial con el password personal del administrador. No guardar tokens en GitHub, en archivos públicos, en HTML o en JavaScript. Configurar secretos mediante un canal seguro y limitar el acceso a las tareas necesarias. Probar primero en staging con acciones de lectura.

La existencia de la guía no significa que la web Vinería del Este esté conectada ni que esta conversación disponga ya de sus herramientas. Tampoco sustituye un instalador de plantillas: gestionar artículos por API y desplegar una plantilla nueva son capacidades distintas que deben comprobarse.

Esta alternativa puede ser útil para el flujo pedido por Pedro: indicar cambios de texto, carta o noticias mientras el asistente los ejecuta. Antes de activarla hay que confirmar la versión instalada, quién administra el servidor y qué operaciones expone la conexión elegida. No activar plugins ni permisos en producción sin inventario y copia de seguridad.

Estado: documentación encontrada; conexión NO configurada ni probada sobre el restaurante.
