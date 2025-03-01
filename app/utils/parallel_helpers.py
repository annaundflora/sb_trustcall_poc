"""
Hilfsfunktionen für kontrollierte Parallelität bei API-Anfragen.

Diese Datei enthält Funktionen zur Steuerung des Parallelitätsgrads bei API-Anfragen,
um das Problem des API-seitigen Queueings zu vermeiden.
"""
import concurrent.futures
from typing import Dict, Any, Callable


def extract_with_limited_concurrency(state: Dict[str, Any], 
                                    extractors: Dict[str, Callable], 
                                    max_workers: int = 2) -> Dict[str, Any]:
    """
    Führt eine begrenzte Anzahl von Extraktoren parallel aus.
    
    Args:
        state: Der aktuelle Zustand des Workflows
        extractors: Ein Dictionary mit Extraktorfunktionen {name: funktion}
        max_workers: Maximale Anzahl gleichzeitiger Anfragen
        
    Returns:
        Ein Dictionary mit den kombinierten Ergebnissen aller Extraktoren
    """
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Starte alle Extraktoren als Future-Objekte
        futures = {executor.submit(extractor, state): name 
                  for name, extractor in extractors.items()}
        
        # Sammle die Ergebnisse, sobald sie verfügbar sind
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                # Füge das Ergebnis zum Gesamtergebnis hinzu
                results.update(future.result())
            except Exception as e:
                # Protokolliere Fehler, aber setze die Verarbeitung fort
                print(f"Fehler bei Extraktor {name}: {str(e)}")
    
    return results


def extract_pickup_group(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert alle Pickup-Adresskomponenten mit begrenzter Parallelität.
    
    Diese Funktion muss importiert werden, nachdem die einzelnen Extraktoren definiert wurden.
    """
    from app.nodes.pickup_address_nodes import (
        extract_pickup_basis,
        extract_pickup_location,
        extract_pickup_time,
        extract_pickup_communication
    )
    
    return extract_with_limited_concurrency(
        state,
        {
            "pickup_basis": extract_pickup_basis,
            "pickup_location": extract_pickup_location,
            "pickup_time": extract_pickup_time,
            "pickup_communication": extract_pickup_communication
        },
        max_workers=2  # Maximal 2 parallele Anfragen
    )


def extract_delivery_group(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert alle Delivery-Adresskomponenten mit begrenzter Parallelität.
    """
    from app.nodes.delivery_address_nodes import (
        extract_delivery_basis,
        extract_delivery_location,
        extract_delivery_time,
        extract_delivery_communication
    )
    
    return extract_with_limited_concurrency(
        state,
        {
            "delivery_basis": extract_delivery_basis,
            "delivery_location": extract_delivery_location,
            "delivery_time": extract_delivery_time,
            "delivery_communication": extract_delivery_communication
        },
        max_workers=2  # Maximal 2 parallele Anfragen
    )


def extract_billing_group(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert alle Billing-Adresskomponenten mit begrenzter Parallelität.
    """
    from app.nodes.billing_address_nodes import (
        extract_billing_basis,
        extract_billing_location,
        extract_billing_communication
    )
    
    return extract_with_limited_concurrency(
        state,
        {
            "billing_basis": extract_billing_basis,
            "billing_location": extract_billing_location,
            "billing_communication": extract_billing_communication
        },
        max_workers=2  # Maximal 2 parallele Anfragen
    )


def extract_shipment_group(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrahiert alle Shipment-Komponenten mit begrenzter Parallelität.
    """
    from app.nodes.shipment_nodes import (
        extract_shipment_basics,
        extract_shipment_dimensions,
        extract_shipment_notes
    )
    
    return extract_with_limited_concurrency(
        state,
        {
            "shipment_basics": extract_shipment_basics,
            "shipment_dimensions": extract_shipment_dimensions,
            "shipment_notes": extract_shipment_notes
        },
        max_workers=2  # Maximal 2 parallele Anfragen
    ) 