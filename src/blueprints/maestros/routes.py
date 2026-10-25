
from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)


def fila_a_diccionario(cursor, fila):
    columnas = [columna[0] for columna in cursor.description]
    maestro = dict(zip(columnas, fila))

    if 'aparterno' in maestro:
        maestro['apaterno'] = maestro.pop('aparterno')

    return maestro


# GET: Listar todos los maestros
@maestros_bp.route("/", methods=['GET'], strict_slashes=False)
def listar_maestros():
    cursor = None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM maestros")
        datos = cursor.fetchall()

        maestros = [
            fila_a_diccionario(cursor, fila)
            for fila in datos
        ]

        return jsonify({
            'maestros': maestros,
            'mensaje': 'Lista de maestros',
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar los maestros {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# GET: Buscar un maestro por ID
@maestros_bp.route("/<string:idmaestro>", methods=['GET'])
def leer_maestro(idmaestro):
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT * FROM maestros WHERE idmaestro=%s",
            (idmaestro,)
        )

        fila = cursor.fetchone()

        if fila is None:
            return jsonify({
                'mensaje': 'Maestro no encontrado',
                'exito': False
            }), 404

        maestro = fila_a_diccionario(cursor, fila)

        return jsonify({
            'maestro': maestro,
            'mensaje': 'Maestro encontrado',
            'exito': True
        }), 200

    except Exception as ex:
        return jsonify({
            'mensaje': 'Error al consultar el maestro {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# POST: Registrar un maestro
@maestros_bp.route("/", methods=['POST'], strict_slashes=False)
def registrar_maestro():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            'mensaje': 'Se requiere un objeto JSON',
            'exito': False
        }), 400

    idmaestro = datos.get('idmaestro')

    campos = [
        'nombre', 'apaterno', 'amaterno', 'correo'
    ]

    if (
        isinstance(idmaestro, bool)
        or not isinstance(idmaestro, (int, str))
        or not str(idmaestro).isdigit()
        or any(
            campo not in datos
            or not isinstance(datos[campo], str)
            or not datos[campo].strip()
            for campo in campos
        )
    ):
        return jsonify({
            'mensaje': 'Faltan campos obligatorios o son invalidos',
            'exito': False
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro=%s",
            (idmaestro,)
        )

        if cursor.fetchone() is not None:
            return jsonify({
                'mensaje': 'El ID del maestro ya existe',
                'exito': False
            }), 409

        sql = """
            INSERT INTO maestros
            (idmaestro, nombre, aparterno, amaterno, correo)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            idmaestro,
            datos['nombre'].strip(),
            datos['apaterno'].strip(),
            datos['amaterno'].strip(),
            datos['correo'].strip()
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro registrado correctamente',
            'exito': True
        }), 201

    except Exception as ex:
        if cursor is not None:
            mysql.connection.rollback()

        return jsonify({
            'mensaje': 'Error al registrar el maestro {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# PUT: Modificar un maestro
@maestros_bp.route("/<string:idmaestro>", methods=['PUT'])
def modificar_maestro(idmaestro):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or not datos:
        return jsonify({
            'mensaje': 'No se recibieron datos para modificar',
            'exito': False
        }), 400

    nombre = datos.get('nombre')
    apaterno = datos.get('apaterno')
    amaterno = datos.get('amaterno')
    correo = datos.get('correo')

    if not all(
        isinstance(campo, str) and campo.strip()
        for campo in [nombre, apaterno, amaterno, correo]
    ):
        return jsonify({
            'mensaje': 'Todos los campos son obligatorios',
            'exito': False
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro=%s",
            (idmaestro,)
        )

        maestro = cursor.fetchone()

        if maestro is None:
            return jsonify({
                'mensaje': 'No existe un maestro con ese ID',
                'exito': False
            }), 404

        sql = """
            UPDATE maestros
            SET nombre=%s,
                aparterno=%s,
                amaterno=%s,
                correo=%s
            WHERE idmaestro=%s
        """

        cursor.execute(sql, (
            nombre.strip(),
            apaterno.strip(),
            amaterno.strip(),
            correo.strip(),
            idmaestro
        ))

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro modificado correctamente',
            'idmaestro': idmaestro,
            'exito': True
        }), 200

    except Exception as ex:
        if cursor is not None:
            mysql.connection.rollback()

        return jsonify({
            'mensaje': 'Error al modificar el maestro {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()


# DELETE: Eliminar un maestro
@maestros_bp.route("/<string:idmaestro>", methods=['DELETE'])
def eliminar_maestro(idmaestro):
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT idmaestro FROM maestros WHERE idmaestro=%s",
            (idmaestro,)
        )

        maestro = cursor.fetchone()

        if maestro is None:
            return jsonify({
                'mensaje': 'No existe un maestro con ese ID',
                'exito': False
            }), 404

        cursor.execute(
            "DELETE FROM maestros WHERE idmaestro=%s",
            (idmaestro,)
        )

        mysql.connection.commit()

        return jsonify({
            'mensaje': 'Maestro eliminado correctamente',
            'idmaestro': idmaestro,
            'exito': True
        }), 200

    except Exception as ex:
        if cursor is not None:
            mysql.connection.rollback()

        return jsonify({
            'mensaje': 'Error al eliminar el maestro {}'.format(ex),
            'exito': False
        }), 500

    finally:
        if cursor is not None:
            cursor.close()
