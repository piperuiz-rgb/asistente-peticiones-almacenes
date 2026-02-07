import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pathlib import Path
import io
import pandas as pd
import openpyxl


@pytest.fixture(autouse=True)
def reset_cart():
    """Reset cart state before each test"""
    from main import cart, catalogs, requests_store, matches
    cart.clear()
    # Don't clear catalogs, requests_store, matches as they don't affect other tests


@pytest.fixture
def test_catalog_data():
    """Sample catalog data for testing"""
    return pd.DataFrame({
        "Referencia": ["[REF001](Rojo, M)", "[REF001](Azul, L)", "[REF002](Verde, S)"],
        "EAN": ["1234567890001", "1234567890002", "1234567890003"],
        "Nombre": ["Producto 1", "Producto 1", "Producto 2"],
        "Color": ["Rojo", "Azul", "Verde"],
        "Talla": ["M", "L", "S"]
    })


@pytest.fixture
def test_request_data():
    """Sample request data for testing"""
    return pd.DataFrame({
        "Producto": ["[REF001](Rojo, M)", "[REF002](Verde, S)", "[REF003](Negro, XL)"],
        "Cantidad": [5, 3, 2]
    })


@pytest.fixture
def test_catalog_file(test_catalog_data):
    """Create a temporary catalog Excel file"""
    buffer = io.BytesIO()
    test_catalog_data.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


@pytest.fixture
def test_request_file(test_request_data):
    """Create a temporary request Excel file"""
    buffer = io.BytesIO()
    test_request_data.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer


@pytest.fixture
def test_catalog_csv(test_catalog_data):
    """Create a temporary catalog CSV file"""
    buffer = io.BytesIO()
    test_catalog_data.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer


@pytest_asyncio.fixture
async def client():
    """Create async HTTP client for testing"""
    from main import app
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
