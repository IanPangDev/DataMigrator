CREATE TABLE dbo.Test (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Name VARCHAR(100) NOT NULL
);

-- Insertar 100 registros de ejemplo
INSERT INTO dbo.Test (Name)
SELECT CONCAT('Name ', number)
FROM master..spt_values
WHERE type = 'P' AND number BETWEEN 1 AND 100;