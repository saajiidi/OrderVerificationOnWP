import pytest
import pandas as pd
from src.utils.product import get_base_product_name, get_size_from_name
from src.utils.text import normalize_city_name, peek_zone_from_address
from src.processing.delivery_parser import parse_amount, is_consignment_id
from src.processing.whatsapp_processor import WhatsAppOrderProcessor


class TestProductUtils:
    def test_get_base_product_name(self):
        assert get_base_product_name("Premium T-Shirt - XL") == "Premium T-Shirt"
        assert get_base_product_name("Plain Product") == "Plain Product"
        assert get_base_product_name("") == ""
        assert get_base_product_name(None) is None

    def test_get_base_product_name_multiple_hyphens(self):
        assert get_base_product_name("Drop Shoulder - Black - L") == "Drop Shoulder - Black"

    def test_get_size_from_name(self):
        assert get_size_from_name("Premium T-Shirt - XL") == "XL"
        assert get_size_from_name("Plain Product") == "N/A"
        assert get_size_from_name("") == "N/A"
        assert get_size_from_name(None) == "N/A"


class TestTextUtils:
    def test_normalize_city_iso_codes(self):
        assert normalize_city_name("BD-13") == "Dhaka"
        assert normalize_city_name("BD-60") == "Sylhet"
        assert normalize_city_name("BD-10") == "Chattogram"

    def test_normalize_city_special_mappings(self):
        assert normalize_city_name("brahmanbaria") == "B. Baria"
        assert normalize_city_name("narsingdi") == "Narshingdi"
        assert normalize_city_name("bogura") == "Bogra"
        assert normalize_city_name("chattogram") == "Chittagong"

    def test_normalize_city_title_case_fallback(self):
        assert normalize_city_name("some city") == "Some City"

    def test_normalize_city_empty(self):
        assert normalize_city_name("") == ""
        assert normalize_city_name(None) == ""

    def test_peek_zone_from_address(self):
        assert peek_zone_from_address("House 10, Mirpur 12, Dhaka") == "Mirpur"
        assert peek_zone_from_address("Sector 4, Uttara, Dhaka") == "Uttara"
        assert peek_zone_from_address("123 Random St, Unknown City") == ""

    def test_peek_zone_empty(self):
        assert peek_zone_from_address("") == ""
        assert peek_zone_from_address(None) == ""
        assert peek_zone_from_address("nan") == ""


class TestDeliveryParser:
    def test_parse_amount(self):
        assert parse_amount("COD 1,250.50") == 1250.50
        assert parse_amount("Charge 60") == 60.0
        assert parse_amount("Discount 0") == 0.0
        assert parse_amount("Random Text") == 0.0

    def test_is_consignment_id(self):
        assert is_consignment_id("DD123456ABC") is True
        assert is_consignment_id("XX999999123") is True
        assert is_consignment_id("D123456ABC") is False
        assert is_consignment_id("NotAnID") is False


class TestWhatsAppProcessor:
    def test_order_aggregation_sum(self):
        processor = WhatsAppOrderProcessor()
        data = {
            "Phone (Billing)": ["01711111111", "01711111111"],
            "Full Name (Billing)": ["John Doe", "John Doe"],
            "Order ID": ["1001", "1001"],
            "Product Name (main)": ["Shirt", "Pants"],
            "Quantity": [1, 2],
            "Item cost": [500, 1000],
            "Order Total Amount": [2500, 2500]  # Total duplicated in raw WooCommerce data
        }
        df = pd.DataFrame(data)
        result_df = processor.process_orders(df)
        
        assert len(result_df) == 1
        assert result_df.iloc[0]["Order Total Amount"] == 2500
        assert "Shirt" in result_df.iloc[0]["Product Name (main)"]
