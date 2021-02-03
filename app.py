from flask import Flask, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
# Modulo para el manejo de SQLALCHEMY
from flask_sqlalchemy import SQLAlchemy
# cifrar contraseñas
from flask_bcrypt import Bcrypt

# PARA MANEJO DE SESIONES

from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail
from flask_mail import Message

import os
# modulo para correo electronico
from flask_mail import Mail
from flask_mail import Message


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.debug = True
Bootstrap(app)
# permito que la aplicacion a traves de la instancia de la clase BCRYPT puede hacer el cifrado
bcrypt = Bcrypt()
bcrypt.init_app(app)
# AQUÍ AGREGUÉ ESTO
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '17460769@colima.tecnm.mx'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# configuracion de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] ='postgres://tcrtawxsrlbgdy:f413df4705461b77d171029054ba79b355ac53427d36b60fc6ecedb2d2114421@ec2-35-175-50-61.compute-1.amazonaws.com:5432/d6gu541krlbrki'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de datos
# 4 Tablas Editorial, Autores, Libros , Usuarios


# Tabla Editorial

class Editorial(db.Model):
    # permite que el nombre de la tabla sea el que se le pasa ''
    __tablename__ = 'editorial'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)  # no puede ser nullo

    def __init__(self, nombre):  # inicializador de un objeto pero actua como un constructor
        self.nombre = nombre

    # def __repr__(self):
      #  return 'La editorial del libro es {}'.format(self.nombre)


# Tabla Libros
class Libros(db.Model):
    __tablename__ = 'libros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(500), nullable=False, index=True)
    clasificacion = db.Column(db.String(80))
    paginas = db.Column(db.Integer)

    id_editorial = db.Column(db.Integer, db.ForeignKey('editorial.id'))
    id_autor = db.Column(db.Integer, db.ForeignKey('autor.id'))

#    def __init__(self, titulo, clasificacion,  paginas, id_editorial, id_autor):
#         self.titulo = titulo

#         self.clasificacion = clasificacion

#         self.paginas = paginas
#         self.id_editorial = id_editorial
#         self.id_autor = id_autor


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)  # no puede ser nullo
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    pwd = db.Column(db.String(255))
    ciudad = db.Column(db.String(150))
    edad = db.Column(db.String(150))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# AQUÍ LO COPIASTE DOS VECES
# LO COMENTÉ Y LO PASÉ BIEN
# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)@login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

# ASÍ ES EL CORRECTO


@login_manager.user_loader
def load_user(user_id):
    # Aquí es tu clase Usuario no User, ya lo corregí
    # return User.get(user_id)
    return Usuario.query.filter_by(id=user_id).first()


class Autor(db.Model):
    __tablename__ = 'autor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)  # no puede ser nullo
    especializacion = db.Column(db.String(80))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/bienvenida')
def bienvenida():
    return render_template("bienvenida.html")


@app.route('/resultado')  # <---Punto de acceso
def resultado():  # <---Nombre de la funcion
    consulta = Usuario.query.all()
    print(consulta)
    # <---Nombre del archivo html
    return render_template("listar.html", variable=consulta)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # QUERY FILTER_BY POR EMAIL
        email = request.form["email"]
        pwd = request.form["pwd"]
        usuario_existe = Usuario.query.filter_by(email=email).first()
        print(usuario_existe)
        # mensaje = usuario_existe.email
        # si lo encuentra entonces
        if usuario_existe != None:
            print("Existe")
            if bcrypt.check_password_hash(usuario_existe.pwd, pwd):
                print("Usuario Autenticado")
                login_user(usuario_existe)
                if current_user.is_authenticated:
                    return redirect("/libros")
        else:
            mensaje = "Usuario no encontrado"
            return render_template("login.html", mensaje=mensaje)
    return render_template("login.html")


@app.route('/editorial')
def editorial():
    return render_template("editorial.html")


@app.route('/libros')
def libros():
    variable0 = Libros.query.all()
    variable1 = Autor.query.all()
    variable2 = Editorial.query.all()
    return render_template("libros.html", variable1=variable1, variable2=variable2, variable0=variable0)


@app.route('/registrarlibro')
def registrarlibro():
    return render_template("registrarlibro.html")


@app.route('/autoregistro')
def autoregistro():
    return render_template("registrarautor.html")

# AQUI ESTOY REGISTRANDO AL USUARIO


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = ""
    if request.method == 'POST':
        pwd = request.form["pwd"]
        password = request.form["password"]

        if pwd != password:
            mensaje = "Las contraseñas no coinciden, intenta de nuevo!"

        else:
            # te crea el usuario en la base de datos
            nombre = request.form["nombre_usuario"]
            correo = request.form["email"]
            pwd = request.form["pwd"]
            ciudad = request.form["ciudad"]
            edad = request.form["edad"]
            print(nombre, correo, pwd, ciudad, edad)
            # crear objeto para el registro del usuario
            usuario = Usuario(
                nombre=nombre,
                email=correo,
                pwd=bcrypt.generate_password_hash(pwd).decode('utf-8'),
                ciudad=ciudad,
                edad=edad
            )
            db.session.add(usuario)
            db.session.commit()
            mensaje = "Usuario registrado!"

            # enviar correo
            msg = Message("Te registraste correctamente",
                          sender="17460769@colima.tecnm.mx", recipients=[correo])
            msg.body = "Bienvenido a la libreria"
            msg.html = "<p> LIBRERIA DIGITAL EL BUEN QUERER TE DA LA BIENVENIDA <p/>"
            mail.send(msg)
            return render_template("registro.html", mensaje=mensaje)
    return render_template("registro.html", mensaje=mensaje)

# AQUI ESTOY REGISTRANDO LA EDITORIAL


@app.route('/registra', methods=['GET', 'POST'])
def registra():
    mensaje = ""

    # te crea la editorial en la base de datos
    nombre = request.form["nombre"]
    print(nombre)
    # crear objeto para el registro del usuario
    editorial = Editorial(
        nombre=nombre)
    db.session.add(editorial)
    db.session.commit()
    mensaje = "Editorial Registrada!"
    return render_template("editorial.html", mensaje=mensaje)
    return render_template("editorial.html", mensaje=mensaje)

# AQUI ESTOY REGISTRANDO AL AUTOR


@app.route('/registraAutor', methods=['GET', 'POST'])
def registraAutor():
    mensaje = ""

    # te crea el autor en la base de datos
    nombre = request.form["nombre"]
    especializacion = request.form["especializacion"]
    print(nombre, especializacion)
    # crear objeto para el registro del usuario
    autor = Autor(
        nombre=nombre,
        especializacion=especializacion
    )

    db.session.add(autor)
    db.session.commit()
    mensaje = "Autor Registrado!"
    return render_template("registrarautor.html", mensaje=mensaje)
    return render_template("registrarautor.html", mensaje=mensaje)

# AQUI ESTOY REGISTRANDO EL LIBRO


@app.route('/registroLibro', methods=['GET', 'POST'])
def registroLibro():
    mensaje = ""

    # te crea el libro en la base de datos
    titulo = request.form["titulo"]
    clasificacion = request.form["clasificacion"]
    paginas = request.form["paginas"]
    print(titulo, clasificacion, paginas)
    # crear objeto para el registro del usuario
    libros = Libros(
        titulo=titulo,
        clasificacion=clasificacion,
        paginas=paginas
    )

    db.session.add(libros)
    db.session.commit()
    mensaje = "Libro Registrado!"
    return render_template("registrarlibro.html", mensaje=mensaje)
    return render_template("registrarlibro.html", mensaje=mensaje)


@app.route('/editar/<id>')
def editar(id):
    resultado = Libros.query.filter_by(id=int(id)).first()
    return render_template("editar.html", resultado=resultado)


@app.route('/eliminar/<id>')
def eliminar(id):
    libros = Libros.query.filter_by(id=int(id)).delete()
    db.session.commit()
    return redirect(url_for('libros'))


@app.route('/actualizar',  methods=['GET', 'POST'])
def actualizar():
    if request.method == "POST":
        consulta = Libros.query.get(request.form['id'])
        consulta.titulo = request.form['titulo']
        # consulta.autor = request.form['autor']
        consulta.clasificacion = request.form['clasificacion']
        consulta.paginas = request.form['paginas']

        db.session.commit()
        return redirect(url_for('libros'))


@app.route('/autores')  # <---Punto de acceso
def autores():  # <---Nombre de la funcion
    consulta = Autor.query.all()
    print(consulta)
    # <---Nombre del archivo html
    return render_template("autor.html", variable=consulta)


if __name__ == '__main__':
    db.create_all()
    app.run()
