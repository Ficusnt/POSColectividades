# POSColectividades
Un Punto de Venta simple en python.

## Cómo usar

1. Abrir `pos.py` con Python 3.
2. La app carga `data/products.csv` y `data/sales.csv`.
3. Menú de productos: podés agregar o eliminar items desde la interfaz.
4. Armar el ticket: seleccioná producto, poné cantidad, agregalo al ticket.
5. Finalizar venta: guarda la venta con timestamp y session_id.
6. Cierre de jornada: muestra total del día.
7. Historial: consultá totales por fecha. Las ventas se recuperan al reabrir porque se guardan en CSV.

## Archivos
- `pos.py` : aplicación principal con Tkinter
- `data/products.csv` : catálogo editable
- `data/sales.csv` : registro de ventas, persistente entre sesiones

## Notas
- Moneda en pesos argentinos, formato con separador de miles.
- Interfaz en español rioplatense.
- No requiere dependencias externas, usa Tkinter estándar.