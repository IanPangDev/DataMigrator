-- Crear la tabla
CREATE TABLE test (
    id INT,
    name STRING
);

-- Insertar 100 filas
INSERT INTO test
SELECT 
    n AS id,
    CONCAT('Name ', n) AS name
FROM (
    SELECT posexplode(split(space(99), ' ')) AS (pos, val)
) tmp
LATERAL VIEW OUTER explode(array(pos + 1)) t AS n;
