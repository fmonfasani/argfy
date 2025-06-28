#!/usr/bin/env python3
# backend/scripts/test_cards_system.py
"""
Script para probar el sistema de Cards Económicas
Ejecutar: python scripts/test_cards_system.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_cards_system():
    """Test completo del sistema de cards"""
    print("🧪 Testing Cards System...")
    
    try:
        from app.services.bcra_service import enhanced_economic_service
        
        async with enhanced_economic_service as service:
            # Test 1: Obtener cards
            print("\n📊 Test 1: Obteniendo cards...")
            cards = await service.get_economic_cards()
            print(f"✅ Cards obtenidas: {len(cards)}")
            
            for card in cards[:3]:  # Mostrar primeras 3
                print(f"  • {card.title}: {card.value} {card.unit} ({card.status.value})")
            
            # Test 2: Datos históricos
            print("\n📈 Test 2: Obteniendo datos históricos...")
            if cards:
                historical = await service.get_historical_data(cards[0].id, 7)
                if "error" not in historical:
                    points = len(historical.get("data_points", []))
                    print(f"✅ Datos históricos obtenidos: {points} puntos")
                else:
                    print(f"❌ Error en históricos: {historical['error']}")
            
            print("\n🎉 Sistema de Cards funcionando correctamente!")
            
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Test de endpoints usando requests"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check: {data.get('status')}")
            print(f"  Cards system: {data.get('cards_system', {}).get('health', 'unknown')}")
        
        # Test cards endpoint (si el servidor está corriendo)
        try:
            response = requests.get(f"{base_url}/api/v1/cards/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cards endpoint: {data.get('total', 0)} cards")
            else:
                print(f"⚠️ Cards endpoint: HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Servidor no está corriendo - start con 'uvicorn app.main:app --reload'")
        
    except ImportError:
        print("⚠️ requests no disponible para test de endpoints")

if __name__ == "__main__":
    # Test async del sistema de cards
    asyncio.run(test_cards_system())
    
    # Test de endpoints (requiere servidor corriendo)
    test_api_endpoints()
    
    print("\n🚀 Para probar completamente:")
    print("1. uvicorn app.main:app --reload")
    print("2. Abrir http://localhost:8000/docs")
    print("3. Probar endpoint /api/v1/cards/")
