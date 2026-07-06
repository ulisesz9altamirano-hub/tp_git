import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

load_dotenv()

app = Flask(__name__)
app.secret_key = "clave_secreta_para_mensajes"

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", ""),
        port=os.getenv("DB_PORT", ""),
        dbname=os.getenv("DB_NAME", ""),       
        user=os.getenv("DB_USER", ""),               
        password=os.getenv("DB_PASSWORD", ""), 
        cursor_factory=RealDictCursor,
    )

@app.route("/")
def index():
    busqueda = request.args.get("buscar", "").strip()
    ordenar_por = request.args.get("ordenar", "fecha_registro")

    columnas_validas = ["apellido", "carrera", "fecha_registro"]
    if ordenar_por not in columnas_validas:
        ordenar_por = "fecha_registro"

    with get_connection() as conn:
        with conn.cursor() as cur:
            if busqueda:
                query = f"""
                    SELECT * FROM estudiantes 
                    WHERE dni ILIKE %s OR apellido ILIKE %s OR carrera ILIKE %s
                    ORDER BY {ordenar_por} ASC
                """
                termino = f"%{busqueda}%"
                cur.execute(query, (termino, termino, termino))
            else:
                query = f"SELECT * FROM estudiantes ORDER BY {ordenar_por} ASC"
                cur.execute(query)
                
            estudiantes = cur.fetchall()

    return render_template("index.html", estudiantes=estudiantes, busqueda=busqueda, ordenar=ordenar_por)



@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        dni = request.form.get("dni", "").strip()
        apellido = request.form.get("apellido", "").strip()
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        carrera = request.form.get("carrera", "").strip()
        telefono = request.form.get("telefono", "").strip()
        edad = request.form.get("edad", "").strip()

        # Validación: Campos obligatorios
        if not dni or not apellido or not nombre or not email or not carrera:
            flash("DNI, Apellido, Nombre, Email y Carrera son campos obligatorios.", "error")
            return redirect(url_for("agregar"))

        # Validación: Formato de Email
        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_email, email):
            flash("Por favor, ingrese un correo electrónico válido (ejemplo@correo.com).", "error")
            return redirect(url_for("agregar"))

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO estudiantes (dni, apellido, nombre, email, carrera, telefono, edad)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (dni, apellido, nombre, email, carrera, telefono if telefono else None, edad if edad else None),
                    )
                conn.commit()
            flash("Estudiante agregado correctamente.", "success")
            return redirect(url_for("index"))
        except psycopg2.errors.UniqueViolation:
            flash("Ya existe un estudiante con ese DNI.", "error")
            return redirect(url_for("agregar"))
        except Exception as e:
            flash(f"Error al agregar estudiante: {e}", "error")
            return redirect(url_for("agregar"))

    # ⚠️ ESTA LÍNEA ES LA CLAVE: Tiene que estar al mismo nivel que el 'if request.method == "POST":'
    return render_template("agregar.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if request.method == "POST":
        dni = request.form.get("dni", "").strip()
        apellido = request.form.get("apellido", "").strip()
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        carrera = request.form.get("carrera", "").strip()
        telefono = request.form.get("telefono", "").strip()
        edad = request.form.get("edad", "").strip()

        if not dni or not apellido or not nombre or not email or not carrera:
            flash("DNI, Apellido, Nombre, Email y Carrera son obligatorios.", "error")
            return redirect(url_for("editar", id=id))

        patron_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(patron_email, email):
            flash("Por favor, ingrese un correo electrónico válido.", "error")
            return redirect(url_for("editar", id=id))

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE estudiantes
                        SET dni=%s, apellido=%s, nombre=%s, email=%s, carrera=%s, telefono=%s, edad=%s
                        WHERE id=%s
                        """,
                        (dni, apellido, nombre, email, carrera, telefono if telefono else None, edad if edad else None, id),
                    )
                conn.commit()
            flash("Estudiante actualizado correctamente.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error al actualizar estudiante: {e}", "error")
            return redirect(url_for("editar", id=id))

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM estudiantes WHERE id = %s", (id,))
            estudiante = cur.fetchone()

    if not estudiante:
        flash("No se encontró el estudiante solicitado.", "error")
        return redirect(url_for("index"))

    return render_template("editar.html", estudiante=estudiante)

@app.route("/eliminar/<int:id>")
def eliminar(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM estudiantes WHERE id = %s", (id,))
        conn.commit()
    flash("Estudiante eliminado correctamente.", "success")
    return redirect(url_for("index"))

@app.route("/about")
def about():
   
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
