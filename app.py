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

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'patagonia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'patagonia_arica_super_secret_2024'
db = SQLAlchemy(app)

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ADMIN_PASSWORD = 'admin123'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.cookies.get('admin_logged_in'):
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

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
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
            login_user(usuario)
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
        email = request.form.get('email', '')
        fecha = request.form['fecha']
        hora = request.form['hora']
        personas = int(request.form['personas'])
        
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
        
        # Otorgar puntos si es usuario registrado
        if current_user.is_authenticated:
            otorgar_puntos_reserva(current_user, reserva)
        
        # Enviar notificaciones
        try:
            resultados = notificar_reserva(reserva)
            if resultados.get('email_cliente') or resultados.get('whatsapp_cliente'):
                flash('¡Reserva enviada! Te hemos enviado una confirmación por email/WhatsApp.')
            else:
                flash('¡Reserva enviada! Será confirmada por el restaurante.')
        except Exception as e:
            print(f"Error enviando notificaciones: {e}")
            flash('¡Reserva enviada! Será confirmada por el restaurante.')
        
        return redirect(url_for('reservas'))
    
    return render_template('reservas.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            resp = redirect(url_for('admin'))
            resp.set_cookie('admin_logged_in', 'true')
            return resp
        else:
            flash('Contraseña incorrecta')
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin():
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
    flash(f'Usuario {usuario.nombre} marcado como administrador')
    return redirect(url_for('admin'))

@app.route('/admin/quitar_admin/<int:usuario_id>')
@admin_required
def quitar_admin(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.is_admin = False
    db.session.commit()
    flash(f'Privilegios de administrador removidos de {usuario.nombre}')
    return redirect(url_for('admin'))

@app.route('/admin/cambiar_password', methods=['GET', 'POST'])
@admin_required
def cambiar_password_admin():
    global ADMIN_PASSWORD
    
    if request.method == 'POST':
        password_actual = request.form['password_actual']
        password_nueva = request.form['password_nueva']
        password_confirmar = request.form['password_confirmar']
        
        # Verificar contraseña actual
        if password_actual != ADMIN_PASSWORD:
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
        
        # Cambiar la contraseña global
        ADMIN_PASSWORD = password_nueva
        
        flash('Contraseña de administrador actualizada exitosamente')
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

# Funciones auxiliares
def verificar_disponibilidad(fecha, hora, personas):
    # Lógica simple: máximo 50 personas por hora
    reservas_existentes = Reserva.query.filter_by(fecha=fecha, hora=hora, estado='confirmada').all()
    total_personas = sum(r.personas for r in reservas_existentes)
    return (total_personas + personas) <= 50

def otorgar_puntos_reserva(usuario, reserva):
    if not reserva.puntos_otorgados:
        puntos = reserva.personas * 10  # 10 puntos por persona
        usuario.puntos += puntos
        reserva.puntos_otorgados = True
        
        # Crear transacción
        transaccion = TransaccionPuntos(
            usuario_id=usuario.id,
            tipo='ganancia',
            puntos=puntos,
            descripcion=f'Reserva para {reserva.personas} personas el {reserva.fecha}'
        )
        db.session.add(transaccion)
        db.session.commit()

def get_configuracion():
    configs = Configuracion.query.all()
    return {config.clave: config.valor for config in configs}

def guardar_configuracion(clave, valor):
    config = Configuracion.query.filter_by(clave=clave).first()
    if config:
        config.valor = valor
    else:
        config = Configuracion(clave=clave, valor=valor)
        db.session.add(config)
    db.session.commit()

@app.route('/descargar_db')
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
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = config['email']
        msg['To'] = usuario.email
        msg['Subject'] = 'Recuperación de Contraseña - Patagonia Raw Bar'
        
        # URL de recuperación
        reset_url = f"http://127.0.0.1:5000/reset_password/{token}"
        
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear configuración inicial
        if not Configuracion.query.first():
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
    
    app.run(debug=True)