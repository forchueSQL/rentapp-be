-- Create a PostgreSQL database schema for an apartment rental application

-- Create the schema
CREATE SCHEMA apartment_rental;

-- Table to store user information (admin, brokers, customers)
CREATE TABLE apartment_rental.users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(15),
    role VARCHAR(20) CHECK (role IN ('admin', 'broker', 'customer')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store property information
CREATE TABLE apartment_rental.properties (
    property_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    property_type VARCHAR(50) CHECK (property_type IN ('apartment', 'house')) NOT NULL,
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    square_feet INTEGER,
    broker_id INTEGER REFERENCES apartment_rental.users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table to store property photos (stored in S3)
CREATE TABLE apartment_rental.property_photos (
    photo_id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES apartment_rental.properties(property_id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for customers to contact brokers
CREATE TABLE apartment_rental.inquiries (
    inquiry_id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES apartment_rental.properties(property_id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES apartment_rental.users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster searches
CREATE INDEX idx_property_city ON apartment_rental.properties(city);
CREATE INDEX idx_property_price ON apartment_rental.properties(price);
CREATE INDEX idx_property_type ON apartment_rental.properties(property_type);

-- Sample data for roles
-- admin: manages the platform
-- broker: uploads property details
-- customer: browses and contacts brokers

-- Add a table for tracking property status (e.g., available, rented)
CREATE TABLE apartment_rental.property_status (
    status_id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES apartment_rental.properties(property_id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('available', 'rented', 'pending')) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
