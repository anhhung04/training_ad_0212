DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    private BOOLEAN NOT NULL DEFAULT 0,
    created_at NOT NULL DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO products (data) VALUES 
    ("{0}",0),
    ("{1}",0),
    ("{2}",0),
    ("{3}",0),
    ("{4}",1);