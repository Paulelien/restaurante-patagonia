#!/usr/bin/env python3
"""
Script para migrar de festivos a promociones especiales
"""

from app import db, app
from sqlalchemy import text

def migrate_to_promociones():
    """Migra de festivos a promociones especiales"""
    with app.app_context():
        print("🔄 Iniciando migración de festivos a promociones...")
        
        # Eliminar tabla de festivos si existe
        try:
            db.session.execute(text("DROP TABLE IF EXISTS festivo"))
            print("✅ Tabla 'festivo' eliminada")
        except Exception as e:
            print(f"⚠️ Error eliminando tabla festivo: {e}")
        
        # Crear nuevas tablas
        try:
            db.create_all()
            print("✅ Nuevas tablas creadas exitosamente")
        except Exception as e:
            print(f"❌ Error creando nuevas tablas: {e}")
            return False
        
        # Verificar que las tablas se crearon correctamente
        try:
            # Verificar tabla promocion_especial
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='promocion_especial'"))
            if result.fetchone():
                print("✅ Tabla 'promocion_especial' creada correctamente")
            else:
                print("❌ Error: Tabla 'promocion_especial' no encontrada")
                return False
            
            # Verificar tabla reserva_promocion
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='reserva_promocion'"))
            if result.fetchone():
                print("✅ Tabla 'reserva_promocion' creada correctamente")
            else:
                print("❌ Error: Tabla 'reserva_promocion' no encontrada")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando tablas: {e}")
            return False
        
        print("🎉 Migración completada exitosamente!")
        print("📋 Nuevas funcionalidades disponibles:")
        print("   - Promociones especiales por fechas")
        print("   - Descuentos personalizados")
        print("   - Puntos extra para 'Nuestra Familia Patagonia'")
        print("   - Menús especiales")
        print("   - Seguimiento de promociones aplicadas")
        
        return True

if __name__ == "__main__":
    migrate_to_promociones() 