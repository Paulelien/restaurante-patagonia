import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from notificaciones import notificar_reserva
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configurar para usar psycopg3 con SQLAlchemy
import psycopg
from psycopg.adapt import Loader

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# Configuración de base de datos para producción
database_url = os.environ.get('DATABASE_URL')
print(f"DEBUG: DATABASE_URL encontrada: {'SÍ' if database_url else 'NO'}")
if database_url and database_url.startswith('postgres'):
    print(f"DEBUG: DATABASE_URL completa: {database_url}")
    # Para producción (PostgreSQL)
    # Render usa postgres:// pero SQLAlchemy necesita postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print("DEBUG: Convertida postgres:// a postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"DEBUG: Usando PostgreSQL en producción: {database_url[:50]}...")
else:
    # Para desarrollo (SQLite)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'patagonia.db')
    print(f"DEBUG: Usando SQLite local: {app.config['SQLALCHEMY_DATABASE_URI']}")

print(f"DEBUG: SQLALCHEMY_DATABASE_URI final: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'patagonia_arica_super_secret_2024')

# Configuración de sesiones para mayor persistencia
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # Sesión válida por 8 horas (jornada laboral)
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Permitir cookies en subdominios
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Renovar sesión en cada request

db = SQLAlchemy(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Eliminamos la contraseña global de admin
# ADMIN_PASSWORD = 'admin123'  # Ya no se usa

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def renovar_sesion_admin():
    """Función para renovar la sesión de administrador"""
    if current_user.is_authenticated and current_user.is_admin:
        session.permanent = True
        session.modified = True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar que el usuario esté autenticado y sea administrador
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Acceso denegado. Se requieren privilegios de administrador.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Modelos de base de datos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    puntos = db.Column(db.Integer, default=0)
    nivel = db.Column(db.String(20), default='Bronce')  # Bronce, Plata, Oro, Diamante
    is_admin = db.Column(db.Boolean, default=False)  # Nuevo campo para administradores
    reset_token = db.Column(db.String(100), unique=True)  # Token para recuperación
    reset_token_expiry = db.Column(db.DateTime)  # Expiración del token
    reservas = db.relationship('Reserva', backref='usuario', lazy=True)
    transacciones = db.relationship('TransaccionPuntos', backref='usuario', lazy=True)

class EmpresaConvenio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    email_contacto = db.Column(db.String(120), nullable=False)
    telefono_contacto = db.Column(db.String(20), nullable=False)
    nombre_contacto = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    numero_empleados = db.Column(db.Integer, default=0)
    descuento_porcentaje = db.Column(db.Integer, default=10)  # Descuento por defecto 10%
    fecha_convenio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='activo')  # activo, inactivo, vencido
    observaciones = db.Column(db.Text)
    eventos = db.relationship('EventoCorporativo', backref='empresa', lazy=True)

class EventoCorporativo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa_convenio.id'), nullable=False)
    nombre_evento = db.Column(db.String(200), nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # almuerzo, cena, coffee break, evento especial
    fecha_evento = db.Column(db.DateTime, nullable=False)
    hora_inicio = db.Column(db.String(10), nullable=False)
    hora_fin = db.Column(db.String(10), nullable=False)
    numero_personas = db.Column(db.Integer, nullable=False)
    lugar_evento = db.Column(db.String(100), default='Restaurante')  # Restaurante, Oficina, Otro
    direccion_evento = db.Column(db.String(200))
    menu_seleccionado = db.Column(db.String(200))
    bebidas_incluidas = db.Column(db.Boolean, default=False)
    servicio_meseros = db.Column(db.Boolean, default=False)
    decoracion = db.Column(db.Boolean, default=False)
    presupuesto_estimado = db.Column(db.Integer)
    descuento_aplicado = db.Column(db.Integer, default=0)
    precio_final = db.Column(db.Integer)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmado, cancelado, completado
    observaciones = db.Column(db.Text)
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_confirmacion = db.Column(db.DateTime)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)  # Ahora es obligatorio
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    personas = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmada, cancelada, completada
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    puntos_otorgados = db.Column(db.Boolean, default=False)

class TransaccionPuntos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ganancia, canje
    puntos = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Configuracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(50), unique=True, nullable=False)
    valor = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.String(200))

class PromocionEspecial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_promocion = db.Column(db.String(50), nullable=False)  # festivo, cumpleaños, aniversario, etc.
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    tipo_descuento = db.Column(db.String(20), default='porcentaje')  # porcentaje, monto_fijo
    valor_descuento = db.Column(db.Float, nullable=False)  # porcentaje o monto
    minimo_personas = db.Column(db.Integer, default=1)
    maximo_personas = db.Column(db.Integer)
    menu_especial = db.Column(db.String(200))
    incluye_bebidas = db.Column(db.Boolean, default=False)
    incluye_postre = db.Column(db.Boolean, default=False)
    puntos_extra = db.Column(db.Integer, default=0)  # puntos extra para "Nuestra Familia Patagonia"
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con reservas que usaron esta promoción
    reservas = db.relationship('ReservaPromocion', backref='promocion', lazy=True)

class ReservaPromocion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=False)
    promocion_id = db.Column(db.Integer, db.ForeignKey('promocion_especial.id'), nullable=False)
    descuento_aplicado = db.Column(db.Float, nullable=False)
    puntos_extra_otorgados = db.Column(db.Integer, default=0)
    fecha_aplicacion = db.Column(db.DateTime, default=datetime.utcnow)

# Rutas principales
@app.route('/')
def inicio():
    config = get_configuracion()
    return render_template('inicio.html', config=config)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado')
            return redirect(url_for('registro'))
        
        usuario = Usuario(
            email=email,
            password_hash=generate_password_hash(password),
            nombre=nombre,
            telefono=telefono
        )
        db.session.add(usuario)
        db.session.commit()
        
        flash('¡Registro exitoso! Ya puedes iniciar sesión.')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario, remember=True)  # Hacer la sesión permanente
            session.permanent = True  # Marcar sesión como permanente
            flash(f'¡Bienvenido, {usuario.nombre}!')
            return redirect(url_for('inicio'))
        else:
            flash('Email o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión')
    return redirect(url_for('inicio'))

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')

@app.route('/reservas', methods=['GET', 'POST'])
def reservas():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form.get('email', '').strip()
        fecha = request.form['fecha']
        hora = request.form['hora']
        personas = int(request.form['personas'])
        
        # Validar que el email sea obligatorio
        if not email:
            flash('El email es obligatorio para enviar la confirmación de la reserva.')
            return redirect(url_for('reservas'))
        
        # Verificar disponibilidad
        if not verificar_disponibilidad(fecha, hora, personas):
            flash('Lo sentimos, no hay disponibilidad para esa fecha y hora.')
            return redirect(url_for('reservas'))
        
        # Crear reserva
        reserva = Reserva(
            usuario_id=current_user.id if current_user.is_authenticated else None,
            nombre=nombre,
            telefono=telefono,
            email=email,
            fecha=fecha,
            hora=hora,
            personas=personas
        )
        db.session.add(reserva)
        db.session.commit()
        
        # Notificar al administrador por email (y WhatsApp si está configurado)
        try:
            from notificaciones import notificar_reserva
            notificar_reserva(reserva, notificar_cliente=False, notificar_admin=True)
        except Exception as e:
            print(f"Error enviando notificación al admin: {e}")
        
        # Aplicar promociones disponibles
        promociones_aplicadas = aplicar_promociones(reserva)
        
        # Otorgar puntos si es usuario registrado
        if current_user.is_authenticated:
            otorgar_puntos_reserva(current_user, reserva)
            # Otorgar puntos extra de promociones
            if promociones_aplicadas:
                for promocion in promociones_aplicadas:
                    if promocion.puntos_extra > 0:
                        otorgar_puntos_extra(current_user, promocion.puntos_extra, f"Promoción: {promocion.nombre}")
        
        # Preparar mensaje de confirmación
        mensaje = '¡Reserva enviada! Será confirmada por el restaurante.'
        if promociones_aplicadas:
            mensaje += f' Se aplicaron {len(promociones_aplicadas)} promoción(es) especial(es).'
        
        flash(mensaje)
        return redirect(url_for('reservas'))
    
    # Obtener promociones activas para mostrar en la página
    promociones_activas = obtener_promociones_activas()
    return render_template('reservas.html', promociones=promociones_activas)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Verificar si existe algún administrador
    try:
        print("DEBUG: Verificando administradores en la base de datos...")
        admin_existente = Usuario.query.filter_by(is_admin=True).first()
        print(f"DEBUG: Admin encontrado: {admin_existente}")
        if admin_existente:
            print(f"DEBUG: Admin encontrado - ID: {admin_existente.id}, Email: {admin_existente.email}, Nombre: {admin_existente.nombre}")
        else:
            print("DEBUG: No se encontró admin, redirigiendo a setup")
            # Si no hay administradores, redirigir a la configuración inicial
            return redirect(url_for('setup_admin'))
    except Exception as e:
        print(f"DEBUG: Error verificando admin: {e}")
        print(f"DEBUG: Tipo de error: {type(e)}")
        # En caso de error, permitir acceso al login
        pass
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        print(f"DEBUG: Intento de login admin - Email: {email}")
        
        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            print(f"DEBUG: Usuario encontrado - ID: {usuario.id}, Is Admin: {usuario.is_admin}")
            if check_password_hash(usuario.password_hash, password):
                if usuario.is_admin:
                    login_user(usuario, remember=True)  # Hacer la sesión permanente
                    session.permanent = True  # Marcar sesión como permanente
                    print(f"DEBUG: Login exitoso para admin: {usuario.nombre}")
                    flash(f'¡Bienvenido, administrador {usuario.nombre}!')
                    return redirect(url_for('admin'))
                else:
                    print(f"DEBUG: Usuario no es admin - Is Admin: {usuario.is_admin}")
                    flash('Acceso denegado. No tienes privilegios de administrador.')
                    return redirect(url_for('admin_login'))
            else:
                print("DEBUG: Contraseña incorrecta")
                flash('Email o contraseña incorrectos')
        else:
            print(f"DEBUG: Usuario no encontrado con email: {email}")
            flash('Email o contraseña incorrectos')
    
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin():
    renovar_sesion_admin()  # Renovar sesión en cada acceso
    reservas = Reserva.query.order_by(Reserva.fecha, Reserva.hora).all()
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).limit(10).all()
    config = get_configuracion()
    return render_template('admin.html', reservas=reservas, usuarios=usuarios, config=config)

@app.route('/admin/confirmar/<int:reserva_id>')
@admin_required
def confirmar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    reserva.estado = 'confirmada'
    db.session.commit()
    
    # Enviar email de confirmación al cliente
    try:
        from notificaciones import Notificaciones
        notif = Notificaciones()
        if reserva.email:
            resultado = notif.enviar_email_confirmacion_cliente(reserva)
            if resultado:
                flash('Reserva confirmada y email enviado al cliente')
            else:
                flash('Reserva confirmada pero error al enviar email')
        else:
            flash('Reserva confirmada (cliente no tiene email registrado)')
    except Exception as e:
        print(f"Error enviando email de confirmación: {e}")
        flash('Reserva confirmada pero error al enviar email')
    
    return redirect(url_for('admin'))

@app.route('/admin/eliminar/<int:reserva_id>')
@admin_required
def eliminar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Solo permitir eliminar reservas pendientes o canceladas
    if reserva.estado not in ['pendiente', 'cancelada']:
        flash('Solo se pueden eliminar reservas pendientes o canceladas')
        return redirect(url_for('admin'))
    
    # Eliminar la reserva
    db.session.delete(reserva)
    db.session.commit()
    
    flash(f'Reserva de {reserva.nombre} eliminada exitosamente')
    return redirect(url_for('admin'))

@app.route('/admin/cancelar/<int:reserva_id>')
@admin_required
def cancelar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    
    # Solo permitir cancelar reservas pendientes o confirmadas
    if reserva.estado not in ['pendiente', 'confirmada']:
        flash('Solo se pueden cancelar reservas pendientes o confirmadas')
        return redirect(url_for('admin'))
    
    # Cambiar estado a cancelada
    reserva.estado = 'cancelada'
    db.session.commit()
    
    flash(f'Reserva de {reserva.nombre} cancelada exitosamente')
    return redirect(url_for('admin'))

@app.route('/admin/configuracion', methods=['GET', 'POST'])
@admin_required
def admin_configuracion():
    if request.method == 'POST':
        # Guardar configuración
        for key in request.form:
            if key.startswith('config_'):
                config_key = key.replace('config_', '')
                valor = request.form[key]
                guardar_configuracion(config_key, valor)
        flash('Configuración actualizada')
        return redirect(url_for('admin_configuracion'))
    
    config = get_configuracion()
    return render_template('admin_configuracion.html', config=config)

@app.route('/admin/marcar_admin/<int:usuario_id>')
@admin_required
def marcar_admin(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.is_admin = True
    db.session.commit()
    flash(f'Usuario {usuario.nombre} marcado como administrador', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/quitar_admin/<int:usuario_id>')
@admin_required
def quitar_admin(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.is_admin = False
    db.session.commit()
    flash(f'Privilegios de administrador removidos de {usuario.nombre}', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/setup', methods=['GET', 'POST'])
def setup_admin():
    """Ruta para crear el primer administrador del sistema"""
    print("DEBUG SETUP: Iniciando setup de administrador")
    
    # Verificar si ya existe algún administrador
    try:
        print("DEBUG SETUP: Verificando si existe admin...")
        admin_existente = Usuario.query.filter_by(is_admin=True).first()
        print(f"DEBUG SETUP: Admin existente: {admin_existente}")
        if admin_existente:
            print(f"DEBUG SETUP: Admin ya existe - ID: {admin_existente.id}, Email: {admin_existente.email}")
            flash('Ya existe un administrador en el sistema')
            return redirect(url_for('admin_login'))
        else:
            print("DEBUG SETUP: No existe admin, continuando con setup")
    except Exception as e:
        print(f"DEBUG SETUP: Error verificando admin: {e}")
        print(f"DEBUG SETUP: Tipo de error: {type(e)}")
        # Continuar con el setup en caso de error
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_confirmar = request.form['password_confirmar']
        nombre = request.form['nombre']
        
        print(f"DEBUG SETUP: Creando admin - Email: {email}, Nombre: {nombre}")
        
        # Verificar que las contraseñas coincidan
        if password != password_confirmar:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('setup_admin'))
        
        # Verificar que el email no esté en uso
        if Usuario.query.filter_by(email=email).first():
            flash('Este email ya está registrado')
            return redirect(url_for('setup_admin'))
        
        try:
            # Crear el administrador
            admin = Usuario(
                email=email,
                password_hash=generate_password_hash(password),
                nombre=nombre,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            
            print(f"DEBUG SETUP: Admin creado exitosamente - ID: {admin.id}")
            flash('Administrador creado exitosamente. Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            print(f"DEBUG SETUP: Error creando admin: {e}")
            db.session.rollback()
            flash('Error al crear el administrador. Intenta nuevamente.')
            return redirect(url_for('setup_admin'))
    
    return render_template('setup_admin.html')

@app.route('/admin/cambiar_password', methods=['GET', 'POST'])
@admin_required
def cambiar_password_admin():
    if request.method == 'POST':
        password_actual = request.form['password_actual']
        password_nueva = request.form['password_nueva']
        password_confirmar = request.form['password_confirmar']
        
        # Verificar contraseña actual del usuario administrador
        if not check_password_hash(current_user.password_hash, password_actual):
            flash('Contraseña actual incorrecta')
            return redirect(url_for('cambiar_password_admin'))
        
        # Verificar que las contraseñas nuevas coincidan
        if password_nueva != password_confirmar:
            flash('Las contraseñas nuevas no coinciden')
            return redirect(url_for('cambiar_password_admin'))
        
        # Verificar que la contraseña nueva no esté vacía
        if not password_nueva.strip():
            flash('La contraseña nueva no puede estar vacía')
            return redirect(url_for('cambiar_password_admin'))
        
        # Cambiar la contraseña del usuario administrador actual
        current_user.password_hash = generate_password_hash(password_nueva)
        db.session.commit()
        
        flash('Contraseña de administrador actualizada exitosamente', 'success')
        return redirect(url_for('admin'))
    
    return render_template('admin_cambiar_password.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']
        flash('¡Mensaje enviado! Pronto nos pondremos en contacto contigo.')
        return redirect(url_for('contacto'))
    return render_template('contacto.html')

# Rutas para Empresas en Convenio y Eventos Corporativos
@app.route('/admin/empresas')
@admin_required
def admin_empresas():
    empresas = EmpresaConvenio.query.order_by(EmpresaConvenio.fecha_convenio.desc()).all()
    return render_template('admin_empresas.html', empresas=empresas)

@app.route('/admin/empresas/nueva', methods=['GET', 'POST'])
@admin_required
def nueva_empresa():
    if request.method == 'POST':
        nombre = request.form['nombre']
        rut = request.form['rut']
        email_contacto = request.form['email_contacto']
        telefono_contacto = request.form['telefono_contacto']
        nombre_contacto = request.form['nombre_contacto']
        direccion = request.form.get('direccion', '')
        numero_empleados = int(request.form.get('numero_empleados', 0))
        descuento_porcentaje = int(request.form.get('descuento_porcentaje', 10))
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        observaciones = request.form.get('observaciones', '')
        
        # Verificar si el RUT ya existe
        if EmpresaConvenio.query.filter_by(rut=rut).first():
            flash('Ya existe una empresa con ese RUT')
            return redirect(url_for('nueva_empresa'))
        
        # Convertir fecha de vencimiento si se proporciona
        fecha_vencimiento_dt = None
        if fecha_vencimiento:
            try:
                fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha inválido')
                return redirect(url_for('nueva_empresa'))
        
        empresa = EmpresaConvenio(
            nombre=nombre,
            rut=rut,
            email_contacto=email_contacto,
            telefono_contacto=telefono_contacto,
            nombre_contacto=nombre_contacto,
            direccion=direccion,
            numero_empleados=numero_empleados,
            descuento_porcentaje=descuento_porcentaje,
            fecha_vencimiento=fecha_vencimiento_dt,
            observaciones=observaciones
        )
        
        db.session.add(empresa)
        db.session.commit()
        
        flash(f'Empresa {nombre} registrada exitosamente')
        return redirect(url_for('admin_empresas'))
    
    return render_template('nueva_empresa.html')

@app.route('/admin/empresas/editar/<int:empresa_id>', methods=['GET', 'POST'])
@admin_required
def editar_empresa(empresa_id):
    empresa = EmpresaConvenio.query.get_or_404(empresa_id)
    
    if request.method == 'POST':
        empresa.nombre = request.form['nombre']
        empresa.email_contacto = request.form['email_contacto']
        empresa.telefono_contacto = request.form['telefono_contacto']
        empresa.nombre_contacto = request.form['nombre_contacto']
        empresa.direccion = request.form.get('direccion', '')
        empresa.numero_empleados = int(request.form.get('numero_empleados', 0))
        empresa.descuento_porcentaje = int(request.form.get('descuento_porcentaje', 10))
        empresa.observaciones = request.form.get('observaciones', '')
        
        fecha_vencimiento = request.form.get('fecha_vencimiento')
        if fecha_vencimiento:
            try:
                empresa.fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha inválido')
                return redirect(url_for('editar_empresa', empresa_id=empresa_id))
        
        db.session.commit()
        flash(f'Empresa {empresa.nombre} actualizada exitosamente')
        return redirect(url_for('admin_empresas'))
    
    return render_template('editar_empresa.html', empresa=empresa)

@app.route('/admin/eventos')
@admin_required
def admin_eventos():
    eventos = EventoCorporativo.query.join(EmpresaConvenio).order_by(EventoCorporativo.fecha_evento.desc()).all()
    return render_template('admin_eventos.html', eventos=eventos)

@app.route('/admin/eventos/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_evento():
    if request.method == 'POST':
        empresa_id = int(request.form['empresa_id'])
        nombre_evento = request.form['nombre_evento']
        tipo_evento = request.form['tipo_evento']
        fecha_evento = request.form['fecha_evento']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        numero_personas = int(request.form['numero_personas'])
        lugar_evento = request.form.get('lugar_evento', 'Restaurante')
        direccion_evento = request.form.get('direccion_evento', '')
        menu_seleccionado = request.form.get('menu_seleccionado', '')
        bebidas_incluidas = 'bebidas_incluidas' in request.form
        servicio_meseros = 'servicio_meseros' in request.form
        decoracion = 'decoracion' in request.form
        presupuesto_estimado = request.form.get('presupuesto_estimado')
        observaciones = request.form.get('observaciones', '')
        
        # Convertir fecha del evento
        try:
            fecha_evento_dt = datetime.strptime(fecha_evento, '%Y-%m-%d')
        except ValueError:
            flash('Formato de fecha inválido')
            return redirect(url_for('nuevo_evento'))
        
        # Obtener empresa y calcular descuento
        empresa = EmpresaConvenio.query.get_or_404(empresa_id)
        descuento_aplicado = empresa.descuento_porcentaje
        
        # Calcular precio final (lógica simplificada)
        precio_base = numero_personas * 15000  # $15,000 por persona como base
        if bebidas_incluidas:
            precio_base += numero_personas * 3000
        if servicio_meseros:
            precio_base += 50000
        if decoracion:
            precio_base += 30000
        
        descuento_monto = int(precio_base * (descuento_aplicado / 100))
        precio_final = precio_base - descuento_monto
        
        evento = EventoCorporativo(
            empresa_id=empresa_id,
            nombre_evento=nombre_evento,
            tipo_evento=tipo_evento,
            fecha_evento=fecha_evento_dt,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            numero_personas=numero_personas,
            lugar_evento=lugar_evento,
            direccion_evento=direccion_evento,
            menu_seleccionado=menu_seleccionado,
            bebidas_incluidas=bebidas_incluidas,
            servicio_meseros=servicio_meseros,
            decoracion=decoracion,
            presupuesto_estimado=presupuesto_estimado,
            descuento_aplicado=descuento_aplicado,
            precio_final=precio_final,
            observaciones=observaciones
        )
        
        db.session.add(evento)
        db.session.commit()
        
        flash(f'Evento {nombre_evento} registrado exitosamente')
        return redirect(url_for('admin_eventos'))
    
    empresas = EmpresaConvenio.query.filter_by(estado='activo').all()
    return render_template('nuevo_evento.html', empresas=empresas)

@app.route('/admin/eventos/confirmar/<int:evento_id>')
@admin_required
def confirmar_evento(evento_id):
    evento = EventoCorporativo.query.get_or_404(evento_id)
    evento.estado = 'confirmado'
    evento.fecha_confirmacion = datetime.utcnow()
    db.session.commit()
    flash(f'Evento {evento.nombre_evento} confirmado exitosamente')
    return redirect(url_for('admin_eventos'))

@app.route('/admin/eventos/cancelar/<int:evento_id>')
@admin_required
def cancelar_evento(evento_id):
    evento = EventoCorporativo.query.get_or_404(evento_id)
    evento.estado = 'cancelado'
    db.session.commit()
    flash(f'Evento {evento.nombre_evento} cancelado')
    return redirect(url_for('admin_eventos'))

# Rutas para gestión de promociones especiales
@app.route('/admin/promociones')
@admin_required
def admin_promociones():
    from datetime import datetime
    promociones = PromocionEspecial.query.order_by(PromocionEspecial.fecha_inicio.desc()).all()
    today = datetime.now().date()
    return render_template('admin_promociones.html', promociones=promociones, today=today)

@app.route('/admin/promociones/nueva', methods=['GET', 'POST'])
@admin_required
def nueva_promocion():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        tipo_promocion = request.form['tipo_promocion']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        tipo_descuento = request.form['tipo_descuento']
        valor_descuento = float(request.form['valor_descuento'])
        minimo_personas = int(request.form.get('minimo_personas', 1))
        maximo_personas = request.form.get('maximo_personas')
        menu_especial = request.form.get('menu_especial', '')
        incluye_bebidas = 'incluye_bebidas' in request.form
        incluye_postre = 'incluye_postre' in request.form
        puntos_extra = int(request.form.get('puntos_extra', 0))
        
        # Validar fechas
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de fecha inválido')
            return redirect(url_for('nueva_promocion'))
        
        if fecha_inicio_dt > fecha_fin_dt:
            flash('La fecha de inicio no puede ser posterior a la fecha de fin')
            return redirect(url_for('nueva_promocion'))
        
        promocion = PromocionEspecial(
            nombre=nombre,
            descripcion=descripcion,
            tipo_promocion=tipo_promocion,
            fecha_inicio=fecha_inicio_dt,
            fecha_fin=fecha_fin_dt,
            tipo_descuento=tipo_descuento,
            valor_descuento=valor_descuento,
            minimo_personas=minimo_personas,
            maximo_personas=maximo_personas if maximo_personas else None,
            menu_especial=menu_especial,
            incluye_bebidas=incluye_bebidas,
            incluye_postre=incluye_postre,
            puntos_extra=puntos_extra
        )
        
        db.session.add(promocion)
        db.session.commit()
        
        flash(f'Promoción "{nombre}" creada exitosamente')
        return redirect(url_for('admin_promociones'))
    
    return render_template('nueva_promocion.html')

@app.route('/admin/promociones/editar/<int:promocion_id>', methods=['GET', 'POST'])
@admin_required
def editar_promocion(promocion_id):
    promocion = PromocionEspecial.query.get_or_404(promocion_id)
    
    if request.method == 'POST':
        promocion.nombre = request.form['nombre']
        promocion.descripcion = request.form['descripcion']
        promocion.tipo_promocion = request.form['tipo_promocion']
        promocion.fecha_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date()
        promocion.fecha_fin = datetime.strptime(request.form['fecha_fin'], '%Y-%m-%d').date()
        promocion.tipo_descuento = request.form['tipo_descuento']
        promocion.valor_descuento = float(request.form['valor_descuento'])
        promocion.minimo_personas = int(request.form.get('minimo_personas', 1))
        promocion.maximo_personas = request.form.get('maximo_personas')
        promocion.menu_especial = request.form.get('menu_especial', '')
        promocion.incluye_bebidas = 'incluye_bebidas' in request.form
        promocion.incluye_postre = 'incluye_postre' in request.form
        promocion.puntos_extra = int(request.form.get('puntos_extra', 0))
        promocion.activo = 'activo' in request.form
        
        db.session.commit()
        flash(f'Promoción "{promocion.nombre}" actualizada exitosamente')
        return redirect(url_for('admin_promociones'))
    
    return render_template('editar_promocion.html', promocion=promocion)

@app.route('/admin/promociones/eliminar/<int:promocion_id>')
@admin_required
def eliminar_promocion(promocion_id):
    promocion = PromocionEspecial.query.get_or_404(promocion_id)
    nombre = promocion.nombre
    db.session.delete(promocion)
    db.session.commit()
    flash(f'Promoción "{nombre}" eliminada exitosamente')
    return redirect(url_for('admin_promociones'))

# Funciones auxiliares
def verificar_disponibilidad(fecha, hora, personas):
    # Lógica simple: máximo 50 personas por hora
    reservas_existentes = Reserva.query.filter_by(fecha=fecha, hora=hora, estado='confirmada').all()
    total_personas = sum(r.personas for r in reservas_existentes)
    return (total_personas + personas) <= 50

def actualizar_nivel_usuario(usuario):
    """Actualiza el nivel del usuario según sus puntos"""
    if usuario.puntos >= 600:
        usuario.nivel = 'Diamante'
    elif usuario.puntos >= 300:
        usuario.nivel = 'Oro'
    elif usuario.puntos >= 100:
        usuario.nivel = 'Plata'
    else:
        usuario.nivel = 'Bronce'
    db.session.commit()

def otorgar_puntos_reserva(usuario, reserva):
    if not reserva.puntos_otorgados:
        puntos = reserva.personas * 10  # 10 puntos por persona
        usuario.puntos += puntos
        reserva.puntos_otorgados = True
        
        # Actualizar nivel del usuario
        actualizar_nivel_usuario(usuario)
        
        # Crear transacción
        transaccion = TransaccionPuntos(
            usuario_id=usuario.id,
            tipo='ganancia',
            puntos=puntos,
            descripcion=f'Reserva para {reserva.personas} personas el {reserva.fecha}'
        )
        db.session.add(transaccion)
        db.session.commit()

def otorgar_puntos_extra(usuario, puntos, descripcion):
    """Otorga puntos extra por promociones"""
    transaccion = TransaccionPuntos(
        usuario_id=usuario.id,
        tipo='ganancia',
        puntos=puntos,
        descripcion=descripcion
    )
    db.session.add(transaccion)
    usuario.puntos += puntos
    db.session.commit()

def aplicar_promociones(reserva):
    """Aplica promociones disponibles a una reserva"""
    from datetime import datetime
    fecha_reserva = datetime.strptime(reserva.fecha, '%Y-%m-%d').date()
    promociones_aplicadas = []
    
    # Obtener promociones activas y vigentes
    promociones = PromocionEspecial.query.filter_by(activo=True).filter(
        PromocionEspecial.fecha_inicio <= fecha_reserva,
        PromocionEspecial.fecha_fin >= fecha_reserva
    ).all()
    
    for promocion in promociones:
        # Verificar condiciones de personas
        if reserva.personas < promocion.minimo_personas:
            continue
        if promocion.maximo_personas and reserva.personas > promocion.maximo_personas:
            continue
        
        # Crear registro de promoción aplicada
        reserva_promocion = ReservaPromocion(
            reserva_id=reserva.id,
            promocion_id=promocion.id,
            descuento_aplicado=promocion.valor_descuento,
            puntos_extra_otorgados=promocion.puntos_extra
        )
        db.session.add(reserva_promocion)
        promociones_aplicadas.append(promocion)
    
    db.session.commit()
    return promociones_aplicadas

def obtener_promociones_activas():
    """Obtiene promociones activas para mostrar en el sitio"""
    from datetime import datetime
    today = datetime.now().date()
    
    promociones = PromocionEspecial.query.filter_by(activo=True).filter(
        PromocionEspecial.fecha_inicio <= today,
        PromocionEspecial.fecha_fin >= today
    ).order_by(PromocionEspecial.fecha_fin.asc()).limit(5).all()
    
    return promociones

def get_configuracion():
    try:
        configs = Configuracion.query.all()
        config_dict = {config.clave: config.valor for config in configs}
        
        # Determinar el horario según el día actual
        from datetime import datetime
        today = datetime.now()
        is_weekend = today.weekday() >= 5  # 5 = Sábado, 6 = Domingo
        
        # Obtener horarios específicos
        horario_semana = config_dict.get('horario_semana', 'Lunes a Viernes: 12:00 - 22:00')
        horario_finde = config_dict.get('horario_finde', 'Sábados y Domingos: 12:00 - 23:00')
        
        # Asignar el horario correcto según el día
        if is_weekend:
            config_dict['horario_actual'] = horario_finde
        else:
            config_dict['horario_actual'] = horario_semana
        
        return config_dict
    except Exception as e:
        print(f"Error obteniendo configuración: {e}")
        # Configuración por defecto si hay error
        return {
            'titulo_sitio': 'Restaurante Patagonia - Arica',
            'descripcion_hero': 'Ubicado en Arica, ofrecemos lo mejor de la gastronomía patagónica en el norte de Chile.',
            'facebook_url': 'https://facebook.com/patagoniaarica',
            'instagram_url': 'https://instagram.com/patagoniaarica',
            'telefono': '+56 58 123 4567',
            'direccion': 'Av. Principal 123, Arica, Chile',
            'horario_semana': 'Lunes a Viernes: 12:00 - 22:00',
            'horario_finde': 'Sábados y Domingos: 12:00 - 23:00',
            'horario_actual': 'Lunes a Viernes: 12:00 - 22:00'
        }

def guardar_configuracion(clave, valor):
    config = Configuracion.query.filter_by(clave=clave).first()
    if config:
        config.valor = valor
    else:
        config = Configuracion(clave=clave, valor=valor)
        db.session.add(config)
    db.session.commit()

@app.route('/descargar_db')
@admin_required
def descargar_db():
    return send_file(os.path.join(basedir, 'patagonia.db'), as_attachment=True)

# Rutas de recuperación de contraseña
@app.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    if request.method == 'POST':
        email = request.form['email']
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            # Generar token de recuperación
            token = secrets.token_urlsafe(32)
            usuario.reset_token = token
            usuario.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
            db.session.commit()
            
            # URL de recuperación
            reset_url = f"http://127.0.0.1:5000/reset_password/{token}"
            
            # Enviar email con el enlace de recuperación
            try:
                enviar_email_recuperacion(usuario, token)
                flash('Se ha enviado un enlace de recuperación a tu email')
                return redirect(url_for('login'))
            except Exception as e:
                print(f"Error enviando email de recuperación: {e}")
                # Mostrar el enlace en pantalla como fallback
                return render_template('recuperar_password.html', reset_url=reset_url, email_error=True)
        else:
            flash('Email no encontrado. Verifica que esté correctamente escrito.')
            return redirect(url_for('login'))
    
    return render_template('recuperar_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    usuario = Usuario.query.filter_by(reset_token=token).first()
    
    if not usuario:
        flash('Enlace de recuperación inválido')
        return redirect(url_for('login'))
    
    if usuario.reset_token_expiry < datetime.utcnow():
        flash('El enlace de recuperación ha expirado')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password_nueva = request.form['password_nueva']
        password_confirmar = request.form['password_confirmar']
        
        if password_nueva != password_confirmar:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('reset_password', token=token))
        
        if len(password_nueva) < 6:
            flash('La contraseña debe tener al menos 6 caracteres')
            return redirect(url_for('reset_password', token=token))
        
        # Actualizar contraseña
        usuario.password_hash = generate_password_hash(password_nueva)
        usuario.reset_token = None
        usuario.reset_token_expiry = None
        db.session.commit()
        
        flash('Contraseña actualizada exitosamente. Ya puedes iniciar sesión.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

def enviar_email_recuperacion(usuario, token):
    """Envía email con enlace de recuperación de contraseña"""
    try:
        from config_email import get_email_config
        config = get_email_config()
        import os
        BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:5000')
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = config['email']
        msg['To'] = usuario.email
        msg['Subject'] = 'Recuperación de Contraseña - Patagonia Raw Bar'
        # URL de recuperación
        reset_url = f"{BASE_URL}/reset_password/{token}"
        # Determinar el tipo de usuario
        user_type = "administrador" if usuario.is_admin else "cliente"
        # Contenido del email
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2d3e50, #34495e); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperación de Contraseña</h1>
                    <p>Patagonia Raw Bar - Cuenta de {user_type.title()}</p>
                </div>
                <div class="content">
                    <h2>¡Hola {usuario.nombre}!</h2>
                    <p>Has solicitado recuperar tu contraseña de {user_type}.</p>
                    <p>Haz clic en el siguiente botón para establecer una nueva contraseña:</p>
                    <a href="{reset_url}" class="btn">🔑 Cambiar Contraseña</a>
                    <p><strong>Importante:</strong></p>
                    <ul>
                        <li>Este enlace expira en 24 horas</li>
                        <li>Si no solicitaste este cambio, ignora este email</li>
                        <li>Tu nueva contraseña debe tener al menos 6 caracteres</li>
                    </ul>
                    <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px; font-size: 12px;">
                        {reset_url}
                    </p>
                    <div class="footer">
                        <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                        <p>© 2024 Patagonia Raw Bar - Arica, Chile</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        # Enviar email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email'], config['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando email de recuperación: {e}")
        return False

@app.route('/admin/estadisticas')
@admin_required
def admin_estadisticas():
    from sqlalchemy import func
    try:
        # ===== ESTADÍSTICAS BÁSICAS =====
        
        # Total de usuarios registrados
        total_usuarios = Usuario.query.count()
        
        # Total de reservas
        total_reservas = Reserva.query.count()
        
        # Total de puntos otorgados
        total_puntos = db.session.query(func.sum(Usuario.puntos)).scalar() or 0
        
        # Promedio de personas por reserva
        promedio_personas = db.session.query(func.avg(Reserva.personas)).scalar() or 0
        
        # Top 10 usuarios con más puntos
        top_usuarios_puntos = Usuario.query.order_by(Usuario.puntos.desc()).limit(10).all()
        
        # ===== DATOS SIMPLIFICADOS =====
        
        # Distribución por niveles de fidelización
        niveles_usuarios = db.session.query(
            Usuario.nivel, func.count(Usuario.id)
        ).group_by(Usuario.nivel).all()
        
        # Reservas por estado
        reservas_por_estado = db.session.query(
            Reserva.estado, func.count(Reserva.id)
        ).group_by(Reserva.estado).all()
        
        # Transacciones de puntos por tipo
        transacciones_puntos = db.session.query(
            TransaccionPuntos.tipo, func.count(TransaccionPuntos.id)
        ).group_by(TransaccionPuntos.tipo).all()
        
        # Distribución de estados de eventos
        estados_eventos = db.session.query(
            EventoCorporativo.estado, func.count(EventoCorporativo.id)
        ).group_by(EventoCorporativo.estado).all()
        
        # ===== DATOS VACÍOS PARA EVITAR ERRORES =====
        usuarios_por_mes = []
        reservas_por_mes = []
        eventos_por_mes = []
        ingresos_por_mes = []
        ranking_empresas = []
        tipos_usuarios = []
        
        return render_template(
            'admin_estadisticas.html',
            # Usuarios
            total_usuarios=total_usuarios,
            usuarios_por_mes=usuarios_por_mes,
            niveles_usuarios=niveles_usuarios,
            tipos_usuarios=tipos_usuarios,
            top_usuarios_puntos=top_usuarios_puntos,
            # Reservas
            total_reservas=total_reservas,
            reservas_por_estado=reservas_por_estado,
            reservas_por_mes=reservas_por_mes,
            promedio_personas=promedio_personas,
            # Fidelización
            total_puntos=total_puntos,
            transacciones_puntos=transacciones_puntos,
            # Eventos
            eventos_por_mes=eventos_por_mes,
            ingresos_por_mes=ingresos_por_mes,
            estados_eventos=estados_eventos,
            ranking_empresas=ranking_empresas
        )
    except Exception as e:
        print(f"Error en estadísticas: {e}")
        # Retornar datos mínimos en caso de error
        return render_template(
            'admin_estadisticas.html',
            total_usuarios=0,
            total_reservas=0,
            total_puntos=0,
            promedio_personas=0,
            top_usuarios_puntos=[],
            niveles_usuarios=[],
            tipos_usuarios=[],
            reservas_por_estado=[],
            transacciones_puntos=[],
            estados_eventos=[],
            usuarios_por_mes=[],
            reservas_por_mes=[],
            eventos_por_mes=[],
            ingresos_por_mes=[],
            ranking_empresas=[]
        )

if __name__ == '__main__':
    with app.app_context():
        try:
            print("DEBUG: Intentando crear tablas de la base de datos...")
            db.create_all()
            print("DEBUG: Tablas creadas exitosamente")
            
            # Verificar conexión consultando una tabla
            try:
                usuarios_count = Usuario.query.count()
                print(f"DEBUG: Conexión exitosa. Usuarios en BD: {usuarios_count}")
            except Exception as e:
                print(f"DEBUG: Error consultando usuarios: {e}")
                
        except Exception as e:
            print(f"DEBUG: Error creando tablas: {e}")
            print(f"DEBUG: Tipo de error: {type(e)}")
        
        # Crear configuración inicial
        try:
            if not Configuracion.query.first():
                print("DEBUG: Creando configuración inicial...")
                configs_iniciales = [
                    ('titulo_sitio', 'Restaurante Patagonia - Arica'),
                    ('descripcion_hero', 'Ubicado en Arica, ofrecemos lo mejor de la gastronomía patagónica en el norte de Chile.'),
                    ('facebook_url', 'https://facebook.com/patagoniaarica'),
                    ('instagram_url', 'https://instagram.com/patagoniaarica'),
                    ('telefono', '+56 58 123 4567'),
                    ('direccion', 'Av. Principal 123, Arica, Chile'),
                    ('horario', 'Lunes a Domingo: 12:00 - 23:00')
                ]
                for clave, valor in configs_iniciales:
                    config = Configuracion(clave=clave, valor=valor)
                    db.session.add(config)
                db.session.commit()
                print("DEBUG: Configuración inicial creada exitosamente")
            else:
                print("DEBUG: Configuración ya existe")
        except Exception as e:
            print(f"DEBUG: Error creando configuración: {e}")
    
    app.run(debug=True)