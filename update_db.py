import os
from app import app, db, Usuario

def actualizar_base_datos():
    with app.app_context():
        # Eliminar la base de datos existente para recrearla con el nuevo esquema
        db_path = os.path.join(os.path.dirname(__file__), 'patagonia.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Base de datos anterior eliminada")
        
        # Crear todas las tablas con el nuevo esquema
        db.create_all()
        print("Nueva base de datos creada con el campo is_admin")
        
        # Marcar el primer usuario como administrador (si existe)
        primer_usuario = Usuario.query.first()
        if primer_usuario:
            primer_usuario.is_admin = True
            db.session.commit()
            print(f"Usuario '{primer_usuario.nombre}' marcado como administrador")
        else:
            print("No hay usuarios en la base de datos")
        
        print("Base de datos actualizada exitosamente")

if __name__ == '__main__':
    actualizar_base_datos() 