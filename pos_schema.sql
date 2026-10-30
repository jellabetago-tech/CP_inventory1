CREATE DATABASE IF NOT EXISTS cp_shop_pos
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE cp_shop_pos;

CREATE TABLE IF NOT EXISTS phone_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model_name VARCHAR(150) NOT NULL,
    imei CHAR(15) NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Available'
);
