import os
from app import db, app

def actualizar_base_datos():
    with app.app_context():
        # Eliminar la base de datos existente para recrearla con el nuevo esquema
        db_path = os.path.join(os.path.dirname(__file__), 'patagonia.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Base de datos anterior eliminada")
        
        # Crear todas las tablas
        db.create_all()
        print("Base de datos actualizada exitosamente!")
        print("Nuevas tablas creadas:")
        print("- empresa_convenio")
        print("- evento_corporativo")

if __name__ == '__main__':
    actualizar_base_datos() 