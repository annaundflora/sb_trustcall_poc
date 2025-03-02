"""
Script to create a clean __init__.py file without null bytes.
"""

with open('app/nodes/__init__.py', 'w', encoding='utf-8') as f:
    f.write('''# Extraction nodes
from app.nodes.fixed_node import extract_shipment_booking

__all__ = [
    "extract_shipment_booking",
]
''') 