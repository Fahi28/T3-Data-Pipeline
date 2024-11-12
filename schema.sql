-- This file should contain table definitions for the database.

SET search_path TO fahad_rahman_schema;

DROP TABLE IF EXISTS fact_transaction;
DROP TABLE IF EXISTS dim_payment_method;
DROP TABLE IF EXISTS dim_truck;

CREATE TABLE dim_payment_method (
    payment_method_id INTEGER GENERATED ALWAYS AS IDENTITY,
    payment_method_type VARCHAR(255),
    PRIMARY KEY (payment_method_id)
);

CREATE TABLE dim_truck (
    truck_id INTEGER GENERATED ALWAYS AS IDENTITY,
    truck_name TEXT NOT NULL,
    truck_description TEXT NOT NULL,
    has_card_reader BOOLEAN NOT NULL,
    fsa_rating SMALLINT,
    PRIMARY KEY (truck_id)
);

CREATE TABLE fact_transaction (
    transaction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    at TIMESTAMP NOT NULL,
    payment_method_id SMALLINT,
    total DECIMAL(10, 2) NOT NULL,
    truck_id BIGINT,
    FOREIGN KEY (payment_method_id) REFERENCES dim_payment_method(payment_method_id),
    FOREIGN KEY (truck_id) REFERENCES dim_truck(truck_id)
);


INSERT INTO dim_payment_method (payment_method_type) VALUES 
('card'),
('cash');

INSERT INTO dim_truck (truck_name, truck_description,
    has_card_reader, fsa_rating) VALUES
    ('Burrito Madness', 'An authentic taste of Mexico.', 1, 4),
    ('Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', 1, 2),
    ('Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', 1, 5),
    ('Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', 1, 4),
    ('Yoghurt Heaven', 'All the great tastes, but only some of the calories!', 1, 4),
    ('SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', 0, 3);