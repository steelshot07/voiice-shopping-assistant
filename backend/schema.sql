CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE brands (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand_id BIGINT NOT NULL REFERENCES brands(id),
    category_id BIGINT NOT NULL REFERENCES categories(id),
    description TEXT,
    size_value NUMERIC(10, 2),
    size_unit VARCHAR(50),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    image_url TEXT,
    available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE shopping_items (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(50),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_user_product
        UNIQUE (user_id, product_id)
);

CREATE TABLE shopping_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity NUMERIC(10, 2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(50),
    purchased_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query VARCHAR(500) NOT NULL,
    brand_id BIGINT REFERENCES brands(id),
    category_id BIGINT REFERENCES categories(id),
    min_price NUMERIC(10, 2) CHECK (min_price >= 0),
    max_price NUMERIC(10, 2) CHECK (max_price >= 0),
    searched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_price_range
        CHECK (
            min_price IS NULL
            OR max_price IS NULL
            OR min_price <= max_price
        )
);

CREATE TABLE user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(20) NOT NULL DEFAULT 'en-IN',
    preferred_brands JSONB NOT NULL DEFAULT '[]'::jsonb,
    preferred_categories JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_shopping_items_user
    ON shopping_items(user_id);

CREATE INDEX idx_shopping_items_product
    ON shopping_items(product_id);

CREATE INDEX idx_shopping_history_user
    ON shopping_history(user_id);

CREATE INDEX idx_shopping_history_product
    ON shopping_history(product_id);

CREATE INDEX idx_search_history_user
    ON search_history(user_id);

CREATE INDEX idx_search_history_searched_at
    ON search_history(searched_at);

CREATE INDEX idx_products_brand
    ON products(brand_id);

CREATE INDEX idx_products_category
    ON products(category_id);

CREATE INDEX idx_products_price
    ON products(price);

CREATE INDEX idx_products_available
    ON products(available);

INSERT INTO categories (name) VALUES
    ('Dairy'),
    ('Produce'),
    ('Bakery'),
    ('Beverages'),
    ('Snacks'),
    ('Personal Care'),
    ('Household'),
    ('Frozen'),
    ('Staples')
ON CONFLICT (name) DO NOTHING;

INSERT INTO brands (name) VALUES
    ('Amul'),
    ('Britannia'),
    ('Colgate'),
    ('Nestle'),
    ('Dove'),
    ('Surf Excel'),
    ('Generic')
ON CONFLICT (name) DO NOTHING;

-- Idempotent product insertion using DO NOTHING via WHERE NOT EXISTS
INSERT INTO products (name, brand_id, category_id, description, size_value, size_unit, price, currency)
SELECT p.name, b.id, c.id, p.description, p.size_value, p.size_unit, p.price, p.currency
FROM (
    VALUES
    -- Produce
    ('Apples', 'Generic', 'Produce', 'Fresh apples', 1, 'kg', 150.00, 'INR'),
    ('Bananas', 'Generic', 'Produce', 'Fresh bananas', 1, 'dozen', 60.00, 'INR'),
    ('Oranges', 'Generic', 'Produce', 'Fresh oranges', 1, 'kg', 80.00, 'INR'),
    ('Mangoes', 'Generic', 'Produce', 'Fresh mangoes', 1, 'kg', 200.00, 'INR'),
    ('Grapes', 'Generic', 'Produce', 'Fresh grapes', 500, 'gram', 90.00, 'INR'),
    ('Tomatoes', 'Generic', 'Produce', 'Fresh tomatoes', 1, 'kg', 40.00, 'INR'),
    ('Potatoes', 'Generic', 'Produce', 'Fresh potatoes', 1, 'kg', 30.00, 'INR'),
    ('Onions', 'Generic', 'Produce', 'Fresh onions', 1, 'kg', 35.00, 'INR'),
    ('Carrots', 'Generic', 'Produce', 'Fresh carrots', 1, 'kg', 50.00, 'INR'),
    ('Spinach', 'Generic', 'Produce', 'Fresh spinach', 1, 'bunch', 20.00, 'INR'),
    ('Cucumber', 'Generic', 'Produce', 'Fresh cucumber', 1, 'kg', 40.00, 'INR'),
    ('Garlic', 'Generic', 'Produce', 'Fresh garlic', 200, 'gram', 60.00, 'INR'),
    ('Ginger', 'Generic', 'Produce', 'Fresh ginger', 200, 'gram', 50.00, 'INR'),
    ('Lemon', 'Generic', 'Produce', 'Fresh lemons', 6, 'pieces', 30.00, 'INR'),
    ('Coriander', 'Generic', 'Produce', 'Fresh coriander leaves', 1, 'bunch', 15.00, 'INR'),
    ('Green Chilies', 'Generic', 'Produce', 'Fresh green chilies', 100, 'gram', 20.00, 'INR'),
    ('Cabbage', 'Generic', 'Produce', 'Fresh green cabbage', 1, 'piece', 40.00, 'INR'),
    ('Cauliflower', 'Generic', 'Produce', 'Fresh cauliflower', 1, 'piece', 50.00, 'INR'),
    ('Capsicum', 'Generic', 'Produce', 'Green bell pepper', 500, 'gram', 60.00, 'INR'),
    ('Mushrooms', 'Generic', 'Produce', 'Button mushrooms', 200, 'gram', 55.00, 'INR'),

    -- Dairy
    ('Milk', 'Amul', 'Dairy', 'Fresh toned milk', 1, 'litre', 68.00, 'INR'),
    ('Curd/Yogurt', 'Amul', 'Dairy', 'Fresh curd', 400, 'gram', 35.00, 'INR'),
    ('Butter', 'Amul', 'Dairy', 'Salted butter', 500, 'gram', 270.00, 'INR'),
    ('Cheese', 'Amul', 'Dairy', 'Cheese slices', 200, 'gram', 140.00, 'INR'),
    ('Paneer', 'Amul', 'Dairy', 'Fresh paneer', 200, 'gram', 90.00, 'INR'),
    ('Eggs', 'Generic', 'Dairy', 'Farm fresh eggs', 6, 'pack', 45.00, 'INR'),
    ('Ice Cream', 'Amul', 'Dairy', 'Vanilla ice cream tub', 1, 'litre', 200.00, 'INR'),

    -- Staples
    ('Rice', 'Generic', 'Staples', 'Basmati rice', 1, 'kg', 120.00, 'INR'),
    ('Wheat flour/Atta', 'Generic', 'Staples', 'Whole wheat atta', 5, 'kg', 220.00, 'INR'),
    ('Maida', 'Generic', 'Staples', 'Refined wheat flour', 1, 'kg', 45.00, 'INR'),
    ('Sugar', 'Generic', 'Staples', 'Refined sugar', 1, 'kg', 50.00, 'INR'),
    ('Salt', 'Generic', 'Staples', 'Iodized salt', 1, 'kg', 25.00, 'INR'),
    ('Toor dal', 'Generic', 'Staples', 'Toor dal / Pigeon pea', 1, 'kg', 160.00, 'INR'),
    ('Moong dal', 'Generic', 'Staples', 'Yellow moong dal', 1, 'kg', 140.00, 'INR'),
    ('Chana dal', 'Generic', 'Staples', 'Split chickpea', 1, 'kg', 100.00, 'INR'),
    ('Cooking oil', 'Generic', 'Staples', 'Refined sunflower oil', 1, 'litre', 130.00, 'INR'),
    ('Olive oil', 'Generic', 'Staples', 'Extra virgin olive oil', 500, 'ml', 450.00, 'INR'),
    ('Pasta', 'Generic', 'Staples', 'Penne pasta', 500, 'gram', 90.00, 'INR'),
    ('Noodles', 'Nestle', 'Staples', 'Instant noodles', 4, 'pack', 56.00, 'INR'),
    ('Ketchup', 'Generic', 'Staples', 'Tomato ketchup', 500, 'gram', 120.00, 'INR'),
    ('Soy sauce', 'Generic', 'Staples', 'Dark soy sauce', 200, 'ml', 65.00, 'INR'),
    ('Jam', 'Generic', 'Staples', 'Mixed fruit jam', 500, 'gram', 160.00, 'INR'),
    ('Honey', 'Generic', 'Staples', 'Pure honey', 500, 'gram', 220.00, 'INR'),

    -- Snacks
    ('Biscuits', 'Britannia', 'Snacks', 'Digestive biscuits', 250, 'gram', 50.00, 'INR'),
    ('Chips', 'Generic', 'Snacks', 'Potato chips', 100, 'gram', 30.00, 'INR'),
    ('Bread', 'Britannia', 'Bakery', 'Whole wheat bread', 400, 'gram', 45.00, 'INR'),
    ('Peanut butter', 'Generic', 'Snacks', 'Creamy peanut butter', 340, 'gram', 150.00, 'INR'),
    ('Cornflakes', 'Generic', 'Snacks', 'Breakfast cereal', 475, 'gram', 180.00, 'INR'),
    ('Chocolate', 'Nestle', 'Snacks', 'Milk chocolate bar', 50, 'gram', 40.00, 'INR'),
    ('Namkeen', 'Generic', 'Snacks', 'Savoury mixture', 200, 'gram', 60.00, 'INR'),

    -- Beverages
    ('Tea', 'Generic', 'Beverages', 'Black tea leaves', 500, 'gram', 250.00, 'INR'),
    ('Coffee', 'Nestle', 'Beverages', 'Instant coffee', 100, 'gram', 320.00, 'INR'),
    ('Green tea', 'Generic', 'Beverages', 'Green tea bags', 25, 'pack', 150.00, 'INR'),
    ('Fruit juice', 'Generic', 'Beverages', 'Mixed fruit juice', 1, 'litre', 110.00, 'INR'),
    ('Bottled water', 'Generic', 'Beverages', 'Packaged drinking water', 1, 'litre', 20.00, 'INR'),
    ('Soda', 'Generic', 'Beverages', 'Carbonated water', 750, 'ml', 40.00, 'INR'),

    -- Household
    ('Dishwashing liquid', 'Generic', 'Household', 'Dish wash gel', 500, 'ml', 105.00, 'INR'),
    ('Laundry detergent', 'Surf Excel', 'Household', 'Washing powder', 1, 'kg', 190.00, 'INR'),
    ('Floor cleaner', 'Generic', 'Household', 'Disinfectant surface cleaner', 1, 'litre', 180.00, 'INR'),
    ('Toilet cleaner', 'Generic', 'Household', 'Liquid toilet cleaner', 500, 'ml', 90.00, 'INR'),
    ('Tissues', 'Generic', 'Household', 'Facial tissues box', 100, 'pulls', 70.00, 'INR'),
    ('Garbage bags', 'Generic', 'Household', 'Medium trash bags', 30, 'pieces', 60.00, 'INR'),
    ('Paper towels', 'Generic', 'Household', 'Kitchen paper towels', 2, 'rolls', 120.00, 'INR'),
    ('Sponge', 'Generic', 'Household', 'Scrub sponge', 3, 'pack', 50.00, 'INR'),

    -- Personal Care
    ('Shampoo', 'Dove', 'Personal Care', 'Hair fall rescue shampoo', 340, 'ml', 320.00, 'INR'),
    ('Conditioner', 'Dove', 'Personal Care', 'Nourishing conditioner', 175, 'ml', 200.00, 'INR'),
    ('Soap', 'Dove', 'Personal Care', 'Beauty bathing bar', 3, 'pack', 160.00, 'INR'),
    ('Body wash', 'Dove', 'Personal Care', 'Moisturizing body wash', 250, 'ml', 190.00, 'INR'),
    ('Toothpaste', 'Colgate', 'Personal Care', 'Strong teeth toothpaste', 150, 'gram', 120.00, 'INR'),
    ('Toothbrush', 'Colgate', 'Personal Care', 'Soft bristle toothbrush', 1, 'piece', 40.00, 'INR'),
    ('Hand wash', 'Generic', 'Personal Care', 'Liquid hand wash', 750, 'ml', 115.00, 'INR'),
    ('Deodorant', 'Generic', 'Personal Care', 'Body spray', 150, 'ml', 200.00, 'INR'),
    ('Shaving cream', 'Generic', 'Personal Care', 'Shaving foam', 200, 'ml', 150.00, 'INR'),
    ('Razors', 'Generic', 'Personal Care', 'Disposable razors', 5, 'pack', 100.00, 'INR')
) AS p(name, brand_name, category_name, description, size_value, size_unit, price, currency)
JOIN brands b ON b.name = p.brand_name
JOIN categories c ON c.name = p.category_name
WHERE NOT EXISTS (
    SELECT 1 FROM products p2 WHERE p2.name = p.name
);