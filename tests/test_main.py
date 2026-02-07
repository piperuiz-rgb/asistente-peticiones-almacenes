import pytest
from httpx import AsyncClient
import io


@pytest.mark.asyncio
async def test_serve_index(client: AsyncClient):
    """Test that the root endpoint serves the index.html"""
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 200
    # The endpoint should return HTML
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_search_products(client: AsyncClient):
    """Test product search functionality"""
    # Search with a query that won't match anything in default catalog
    response = await client.get("/products/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_upload_catalog(client: AsyncClient, test_catalog_file):
    """Test catalog upload"""
    files = {"file": ("catalog.xlsx", test_catalog_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = await client.post("/catalog/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "catalog_id" in data
    assert "rows" in data
    assert data["rows"] == 3


@pytest.mark.asyncio
async def test_upload_catalog_csv(client: AsyncClient, test_catalog_csv):
    """Test catalog upload with CSV format"""
    files = {"file": ("catalog.csv", test_catalog_csv, "text/csv")}
    response = await client.post("/catalog/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "catalog_id" in data
    assert data["rows"] == 3


@pytest.mark.asyncio
async def test_upload_request(client: AsyncClient, test_request_file):
    """Test request upload"""
    files = {"file": ("request.xlsx", test_request_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = await client.post("/request/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert "rows" in data
    assert data["rows"] == 3


@pytest.mark.asyncio
async def test_match_catalog_request(client: AsyncClient, test_catalog_file, test_request_file):
    """Test matching catalog with request"""
    # Upload catalog
    files = {"file": ("catalog.xlsx", test_catalog_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    cat_response = await client.post("/catalog/upload", files=files)
    catalog_id = cat_response.json()["catalog_id"]
    
    # Upload request
    test_request_file.seek(0)  # Reset buffer
    files = {"file": ("request.xlsx", test_request_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    req_response = await client.post("/request/upload", files=files)
    request_id = req_response.json()["request_id"]
    
    # Perform match
    match_response = await client.post("/match", json={
        "catalog_id": catalog_id,
        "request_id": request_id
    })
    
    assert match_response.status_code == 200
    data = match_response.json()
    assert "match_id" in data
    assert "total" in data
    assert "encontrados" in data
    assert "no_encontrados" in data
    assert "preview" in data
    assert data["total"] == 3
    assert data["encontrados"] == 2  # REF001 and REF002 should match
    assert data["no_encontrados"] == 1  # REF003 should not match


@pytest.mark.asyncio
async def test_match_export(client: AsyncClient, test_catalog_file, test_request_file):
    """Test exporting match results"""
    # Upload catalog
    files = {"file": ("catalog.xlsx", test_catalog_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    cat_response = await client.post("/catalog/upload", files=files)
    catalog_id = cat_response.json()["catalog_id"]
    
    # Upload request
    test_request_file.seek(0)
    files = {"file": ("request.xlsx", test_request_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    req_response = await client.post("/request/upload", files=files)
    request_id = req_response.json()["request_id"]
    
    # Perform match
    match_response = await client.post("/match", json={
        "catalog_id": catalog_id,
        "request_id": request_id
    })
    match_id = match_response.json()["match_id"]
    
    # Export all results as XLSX
    export_response = await client.get(f"/match/{match_id}/export?format=xlsx&type=all")
    assert export_response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in export_response.headers["content-type"]
    
    # Export missing results as CSV
    export_csv_response = await client.get(f"/match/{match_id}/export?format=csv&type=missing")
    assert export_csv_response.status_code == 200
    assert "text/csv" in export_csv_response.headers["content-type"]


@pytest.mark.asyncio
async def test_match_not_found(client: AsyncClient):
    """Test match with invalid IDs"""
    response = await client.post("/match", json={
        "catalog_id": "invalid_id",
        "request_id": "invalid_id"
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cart_add(client: AsyncClient):
    """Test adding items to cart"""
    response = await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 2
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "items" in data


@pytest.mark.asyncio
async def test_cart_remove(client: AsyncClient):
    """Test removing items from cart"""
    # Add item first
    await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 3
    })
    
    # Remove some quantity
    response = await client.post("/cart/remove", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


@pytest.mark.asyncio
async def test_cart_view(client: AsyncClient):
    """Test viewing cart contents"""
    # Add items to cart
    await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 2
    })
    
    await client.post("/cart/add", json={
        "ref": "REF002",
        "color": "Azul",
        "talla": "L",
        "qty": 1
    })
    
    # View cart
    response = await client.get("/cart/view")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_cart_checkout_csv(client: AsyncClient):
    """Test checkout with CSV format"""
    # Add items to cart
    await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 5
    })
    
    # Checkout
    response = await client.get(
        "/cart/checkout",
        params={
            "format": "csv",
            "origin": "Almacén A",
            "destination": "Almacén B",
            "fecha": "2026-02-07",
            "pedido_ref": "PED-001"
        }
    )
    
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_cart_checkout_xlsx(client: AsyncClient):
    """Test checkout with XLSX format"""
    # Add items to cart
    await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 3
    })
    
    # Checkout
    response = await client.get(
        "/cart/checkout",
        params={
            "format": "xlsx",
            "origin": "Almacén A",
            "destination": "Almacén B",
            "fecha": "2026-02-07",
            "pedido_ref": "PED-002"
        }
    )
    
    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_upload_unsupported_format(client: AsyncClient):
    """Test uploading a file with unsupported format"""
    # Create a fake file with unsupported extension
    fake_file = io.BytesIO(b"fake content")
    files = {"file": ("test.txt", fake_file, "text/plain")}
    
    response = await client.post("/catalog/upload", files=files)
    assert response.status_code == 400
    assert "Formato no soportado" in response.json()["detail"]


@pytest.mark.asyncio
async def test_cart_add_negative_quantity(client: AsyncClient):
    """Test adding negative quantity removes items"""
    # Add item first
    await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": 5
    })
    
    # Add negative quantity (should reduce)
    response = await client.post("/cart/add", json={
        "ref": "REF001",
        "color": "Rojo",
        "talla": "M",
        "qty": -3
    })
    
    assert response.status_code == 200
    
    # View cart to verify
    cart_response = await client.get("/cart/view")
    items = cart_response.json()["items"]
    # Should still have 2 items (5 - 3)
    matching_item = [item for item in items if item["ref"] == "REF001"]
    if matching_item:
        assert matching_item[0]["qty"] == 2
