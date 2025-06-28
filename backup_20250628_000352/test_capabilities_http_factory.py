#!/usr/bin/env python3
# quick_test.py - Test rápido de capacidades HTTP

import sys
sys.path.insert(0, '.')

def quick_test():
    print("🧪 QUICK TEST - HTTP Capabilities")
    print("=" * 40)
    
    try:
        from app.services.http_factory import HTTPClientFactory
        caps = HTTPClientFactory.get_capabilities()
        print("✅ HTTP Factory funcionando")
        print(f"📊 Capacidades: {caps}")
        
        for use_case in ["scraping", "modern_api", "massive_parallel"]:
            try:
                client_class, client_type = HTTPClientFactory.get_best_client(use_case)
                print(f"  • {use_case}: {client_type.value}")
            except Exception as e:
                print(f"  • {use_case}: ERROR - {e}")
                
    except Exception as e:
        print(f"❌ HTTP Factory error: {e}")
    
    # Test unified service
    try:
        from app.services.unified_service import unified_service
        print("✅ Unified Service disponible")
    except Exception as e:
        print(f"❌ Unified Service error: {e}")
    
    print("\n🎯 RESULTADO:")
    print("Si ves '✅ HTTP Factory funcionando' tu stack híbrido está listo!")

if __name__ == "__main__":
    quick_test()
