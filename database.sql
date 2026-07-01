CREATE TABLE IF NOT EXISTS estudiantes (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(15) NOT NULL UNIQUE,
    apellido VARCHAR(100) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    edad INT,
    email VARCHAR(120),
    carrera VARCHAR(120),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO estudiantes (dni, apellido, nombre, telefono, edad, email, carrera) VALUES
('30111222', 'Pérez', 'María', '2615551234', 22, 'maria.perez@email.com', 'Tecnicatura en Desarrollo de Software'),
('32222333', 'Gómez', 'Juan', '2615555678', 25, 'juan.gomez@email.com', 'Tecnicatura en Desarrollo de Software'),
('34333444', 'Rodríguez', 'Ana', '2615559012', 20, 'ana.rodriguez@email.com', 'Programación')
ON CONFLICT (dni) DO NOTHING;