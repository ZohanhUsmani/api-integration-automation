import pytest
from unittest.mock import patch, MagicMock
from src.client import APIClient


def test_paginate_page_strategy():
    client = APIClient("https://api.example.com", rps=100)
    page1 = MagicMock()
    page1.json.return_value = {"data": [{"id": 1}, {"id": 2}], "total": 2}
    page1.raise_for_status = lambda: None
    with patch.object(client.session, "request", return_value=page1):
        items = client.paginate("/items", strategy="page", per_page=2)
    assert len(items) == 2
    assert items[0]["id"] == 1