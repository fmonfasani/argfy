# scripts/test_bcra_integration.py
import asyncio
import json
from app.services.bcra_real_data_service import BCRARealDataService

async def test_complete_integration():
    print("🧪 TESTING INTEGRACIÓN COMPLETA BCRA")
    print("="*50)
    
    async with BCRARealDataService() as service:
        
        # Test 1: Variables Monetarias
        print("\n📊 Test 1: Variables Monetarias")
        variables = await service.get_variables_monetarias()
        if variables.get("status") == "success":
            print(f"✅ {len(variables.get('variables', {}))} variables obtenidas")
            
            # Mostrar variables clave
            for key, data in variables.get("variables", {}).items():
                print(f"  • {key}: {data['valor']} ({data['fecha']})")
        else:
            print(f"❌ Error: {variables}")
        
        # Test 2: Cotizaciones
        print("\n💱 Test 2: Cotizaciones")
        cotizaciones = await service.get_cotizaciones_oficiales()
        if cotizaciones.get("status") == "success":
            print(f"✅ {len(cotizaciones.get('cotizaciones', {}))} cotizaciones")
            
            # Mostrar principales
            principales = ["USD", "EUR", "GBP", "BRL"]
            for moneda in principales:
                if moneda in cotizaciones.get("cotizaciones", {}):
                    data = cotizaciones["cotizaciones"][moneda]
                    print(f"  • {moneda}: ${data['cotizacion']}")
        else:
            print(f"❌ Error: {cotizaciones}")
        
        # Test 3: Dashboard Completo
        print("\n🎯 Test 3: Dashboard Completo")
        dashboard = await service.get_dashboard_data()
        if dashboard.get("status") == "success":
            print("✅ Dashboard generado exitosamente")
            
            # Mostrar estructura
            indicadores = len(dashboard.get("indicadores_principales", {}))
            cotiz = len(dashboard.get("cotizaciones", {}))
            print(f"  • Indicadores principales: {indicadores}")
            print(f"  • Cotizaciones: {cotiz}")
            
            # Guardar ejemplo
            with open("dashboard_example.json", "w") as f:
                json.dump(dashboard, f, indent=2, default=str)
            print("  • Ejemplo guardado en dashboard_example.json")
        else:
            print(f"❌ Error: {dashboard}")
        
        # Test 4: Datos Históricos
        print("\n📈 Test 4: Datos Históricos (USD)")
        historicos = await service.get_variable_historica(5, 7)  # USD últimos 7 días
        if historicos.get("status") == "success":
            datos = historicos.get("datos", [])
            print(f"✅ {len(datos)} puntos históricos obtenidos")
            
            # Mostrar últimos 3
            for item in datos[-3:]:
                print(f"  • {item['fecha']}: ${item['valor']}")
        else:
            print(f"❌ Error: {historicos}")

if __name__ == "__main__":
    asyncio.run(test_complete_integration())