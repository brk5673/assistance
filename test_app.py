import pytest
import json
import os
from app import catalog, EventHandler
from unittest.mock import patch

def test_catalog_json_loading():
    """Ensure that catalog.json is read correctly and contains the expected structure."""
    with open("catalog.json", "r") as f:
        data = json.load(f)
    assert isinstance(data, list), "Catalog should be a list"
    assert len(data) > 0, "Catalog should not be empty"
    required_fields = ["PRODUCT_ID", "Name", "Description", "Price", "Stock_availabiility"]
    for product in data:
        assert isinstance(product, dict), "Each product should be a dictionary"
        assert required_fields == list(product.keys()), "Each product should have the required fields"
        assert isinstance(product["PRODUCT_ID"], int), "PRODUCT_ID should be int"
        assert isinstance(product["Name"], str), "Name should be str"
        assert isinstance(product["Description"], str), "Description should be str"
        assert isinstance(product["Price"], (int, float)), "Price should be int/float"
        assert isinstance(product["Stock_availabiility"], int), "Stock_availabiility should be int"

def test_openai_api_key_configured():
    """Ensure that the environment variable OPENAI_API_KEY is set."""
    api_key = os.getenv("OPENAI_API_KEY")
    assert api_key is not None and api_key != "", "OPENAI_API_KEY must be configured"

#5.1. Catalog Loading Test
@pytest.mark.parametrize("product", catalog)
def test_catalog_loading(product):
    '''Ensure that the catalog is loaded correctly and contains the expected products'''
    assert isinstance(catalog, list), "Catalog should be a list"
    assert len(catalog) > 0, "Catalog should not be empty"

    required_fields = ["PRODUCT_ID", "Name", "Description", "Price", "Stock_availabiility"]

    for product in catalog:
        assert isinstance(product, dict), "Each product should be a dictionary"
        assert required_fields == list(product.keys()), "Each product should have the required fields"
        assert isinstance(product["PRODUCT_ID"], int), f"PRODUCT_ID should be int, found {type(product['PRODUCT_ID'])}"
        assert isinstance(product["Name"], str), f"Name should be str, found {type(product['Name'])}"
        assert isinstance(product["Description"], str), f"Description should be str, found {type(product['Description'])}"
        assert isinstance(product["Price"], (int, float)), f"Price should be int/float, found {type(product['Price'])}"
        assert isinstance(product["Stock_availabiility"], int), f"Stock_availabiility should be int, found {type(product['Stock_availabiility'])}"

#5.2. Function get_all_products Test
def test_get_all_products():
    '''Ensure that get_all_products returns the correct list of products'''
    response = EventHandler.get_all_products()
    assert response.startswith("The available products are:"), "Response format is incorrect"

    products_names = [product["Name"] for product in catalog]
    for name in products_names:
        assert name in response, f"Missing product: ${name}"

#5.3. Function get_product_info Test
@pytest.mark.parametrize("product", catalog)
def test_get_product_info_existing(product):
    """ Ensure that the function returns correct info for existing products. """
    expected_output = f"The product is {product['Name']} with description: {product['Description']} and price: {product['Price']}."
    assert EventHandler.get_product_info(product["Name"]) == expected_output

def test_get_product_info_non_existent():
    """ Ensure the function handles non-existent products correctly. """
    assert EventHandler.get_product_info("NonExistentProduct") == "Product not found."

#5.4. Function get_product_stock Test
@pytest.mark.parametrize("product", catalog)
def test_get_product_stock_existing(product):
    """ Ensure that the function correctly reports stock availability for existing products. """
    expected_output = f"The product {product['Name']} is in stock with availability: {product['Stock_availabiility']}."
    assert EventHandler.get_product_stock(product["Name"]) == expected_output

def test_get_product_stock_non_existent():
    """ Ensure the function handles non-existent products correctly. """
    assert EventHandler.get_product_stock("NonExistentProduct") == "Product not found."

def test_get_product_stock_zero():
    """Ensure that a product with 0 stock is handled correctly."""
    dummy_product = {
        "PRODUCT_ID": 999,
        "Name": "ZeroStockProduct",
        "Description": "Dummy product with no stock",
        "Price": 100,
        "Stock_availabiility": 0
    }
    with patch('app.catalog', new=catalog + [dummy_product]):
        expected_output = f"The product {dummy_product['Name']} is in stock with availability: {dummy_product['Stock_availabiility']}."
        assert EventHandler.get_product_stock(dummy_product["Name"]) == expected_output

#5.5. Complete Interaction Flow Test
def test_complete_interaction_flow():
    """ Simulates a complete user session and verifies the correct function calls. """
    user_inputs = iter(["I want to buy a Laptop", "END"])

    with patch("builtins.input", lambda _: next(user_inputs)):
        with patch("app.EventHandler.get_product_info") as mock_get_product_info:
            mock_get_product_info.return_value = "Mocked Product Info"
            response = EventHandler.get_product_info("Laptop")

    assert response == "Mocked Product Info"

#5.6. Error Handling and Edge Cases
@pytest.mark.parametrize("invalid_input", ["", "!!@@###", "NonExistentProductXYZ"])
def test_invalid_product_info(invalid_input):
    """ Ensure that invalid product names return 'Product not found.' """
    assert EventHandler.get_product_info(invalid_input) == "Product not found."

@pytest.mark.parametrize("invalid_input", ["", "!!@@###", "NonExistentProductXYZ"])
def test_invalid_product_stock(invalid_input):
    """ Ensure that invalid product names return 'Product not found.' for stock check """
    assert EventHandler.get_product_stock(invalid_input) == "Product not found."