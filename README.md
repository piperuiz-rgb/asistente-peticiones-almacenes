# Asistente de Peticiones de Almacenes

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Descripción

Aplicación web para la gestión de peticiones de almacenes, permitiendo cargar catálogos de productos, gestionar peticiones, realizar coincidencias entre catálogos y peticiones, y generar órdenes de compra. El sistema incluye un carrito de compras manual para facilitar la creación de pedidos personalizados.

## Características

- 🔍 Búsqueda de productos en el catálogo
- 📤 Carga de catálogos y peticiones desde archivos Excel/CSV
- 🔄 Coincidencia automática entre catálogos y peticiones
- 🛒 Carrito de compras manual
- 📊 Exportación de resultados en formato Excel/CSV
- 🎨 Interfaz web moderna y responsive

## Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/piperuiz-rgb/asistente-peticiones-almacenes.git
cd asistente-peticiones-almacenes
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Cómo Ejecutar

### Modo Desarrollo

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La aplicación estará disponible en: `http://localhost:8000`

### Modo Producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Con Docker

```bash
docker-compose up
```

La aplicación estará disponible en: `http://localhost:8000`

## Documentación de la API

Una vez ejecutada la aplicación, puedes acceder a la documentación interactiva de la API:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints Disponibles

### Catálogo

- **POST** `/catalog/upload` - Cargar un archivo de catálogo (Excel/CSV)
  - Parámetros: `file` (multipart/form-data)
  - Respuesta: `{ "catalog_id": "...", "rows": 100 }`

### Peticiones

- **POST** `/request/upload` - Cargar un archivo de petición (Excel/CSV)
  - Parámetros: `file` (multipart/form-data)
  - Respuesta: `{ "request_id": "...", "rows": 50 }`

### Coincidencias

- **POST** `/match` - Realizar coincidencia entre catálogo y petición
  - Body: `{ "catalog_id": "...", "request_id": "..." }`
  - Respuesta: Estadísticas de coincidencias y preview de resultados

- **GET** `/match/{match_id}/export?format=xlsx&type=all` - Exportar resultados
  - Parámetros: 
    - `format`: `xlsx` o `csv`
    - `type`: `all` (todos) o `missing` (no encontrados)

### Búsqueda

- **GET** `/products/search?q={query}` - Buscar productos en el catálogo
  - Parámetros: `q` (texto de búsqueda)
  - Respuesta: Lista de productos con variantes

### Carrito

- **POST** `/cart/add` - Añadir producto al carrito
  - Body: `{ "ref": "...", "color": "...", "talla": "...", "qty": 1 }`

- **POST** `/cart/remove` - Eliminar producto del carrito
  - Body: `{ "ref": "...", "color": "...", "talla": "...", "qty": 1 }`

- **GET** `/cart/view` - Ver contenido del carrito
  - Respuesta: `{ "items": [...] }`

- **GET** `/cart/checkout` - Generar pedido desde el carrito
  - Parámetros: 
    - `format`: `xlsx` o `csv`
    - `origin`: Almacén de origen
    - `destination`: Almacén de destino
    - `fecha`: Fecha del pedido
    - `pedido_ref`: Referencia del pedido

## Estructura del Proyecto

```
asistente-peticiones-almacenes/
├── main.py                  # Aplicación principal FastAPI
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Dependencias de desarrollo
├── catalogue.xlsx           # Catálogo por defecto (opcional)
├── plantilla_pedido.xlsx    # Plantilla de pedido (opcional)
├── static/                  # Archivos estáticos
│   └── index.html          # Interfaz web
├── tests/                   # Tests
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── Dockerfile              # Configuración Docker
├── docker-compose.yml      # Configuración Docker Compose
├── .dockerignore
├── .gitignore
├── .env.example            # Ejemplo de variables de entorno
├── LICENSE                 # Licencia MIT
└── README.md              # Este archivo
```

## Formato de Archivos

### Catálogo

El archivo de catálogo debe contener al menos las siguientes columnas:
- `Referencia` o primera columna: Código de producto (puede incluir formato `[REF](COLOR, TALLA)`)
- `EAN` o `CodBarras`: Código de barras
- `Color` (opcional): Color del producto
- `Talla` (opcional): Talla del producto
- `Nombre` (opcional): Nombre del producto

### Petición

El archivo de petición debe contener:
- Primera columna: Producto (formato `[REF](COLOR, TALLA)`)
- `Cantidad` o tercera columna: Cantidad solicitada

## Ejemplos de Uso

### 1. Cargar catálogo y petición

```bash
curl -X POST "http://localhost:8000/catalog/upload" \
  -F "file=@mi_catalogo.xlsx"

curl -X POST "http://localhost:8000/request/upload" \
  -F "file=@mi_peticion.xlsx"
```

### 2. Realizar coincidencia

```bash
curl -X POST "http://localhost:8000/match" \
  -H "Content-Type: application/json" \
  -d '{"catalog_id": "abc123", "request_id": "xyz789"}'
```

### 3. Buscar productos

```bash
curl "http://localhost:8000/products/search?q=camisa"
```

## Tests

### Ejecutar tests

```bash
pytest
```

### Con cobertura

```bash
pytest --cov=. --cov-report=html
```

## Desarrollo

### Instalar dependencias de desarrollo

```bash
pip install -r requirements-dev.txt
```

### Ejecutar linter

```bash
ruff check .
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Autor

**piperuiz-rgb**

## Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un [issue](https://github.com/piperuiz-rgb/asistente-peticiones-almacenes/issues).
