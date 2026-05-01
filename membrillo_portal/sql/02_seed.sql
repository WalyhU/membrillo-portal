-- Seed realista "El Membrillo"
USE membrillo_db;

INSERT INTO tipo_producto (id, nombre, descripcion) VALUES
  (1, 'Jaleas',     'Jaleas artesanales de fruta'),
  (2, 'Mermeladas', 'Mermeladas artesanales con trozos de fruta'),
  (3, 'Conservas',  'Conservas y dulces de membrillo'),
  (4, 'Almibares',  'Frutas en almibar artesanales');

INSERT INTO producto (id, tipo_id, nombre, descripcion, precio, imagen_url, activo) VALUES
  (1, 1, 'Jalea de Membrillo 250g',  'Producto estrella. Receta tradicional Guzman 40+ anios.', 35.00, '/static/img/jalea_membrillo.jpg', 1),
  (2, 1, 'Jalea de Fresa 250g',      'Fresa fresca de Sacatepequez.',                              30.00, '/static/img/jalea_fresa.jpg',     1),
  (3, 1, 'Jalea de Mora 250g',       'Mora silvestre del altiplano.',                              32.00, '/static/img/jalea_mora.jpg',      1),
  (4, 1, 'Jalea de Manzana 250g',    'Manzana criolla.',                                           28.00, '/static/img/jalea_manzana.jpg',   1),
  (5, 2, 'Mermelada de Durazno 300g','Mermelada con trozos de durazno.',                           38.00, '/static/img/merm_durazno.jpg',    1),
  (6, 3, 'Conserva de Membrillo 500g','Bloque tradicional para postres.',                          55.00, '/static/img/conserva_membrillo.jpg',1),
  (7, 4, 'Almibar de Membrillo 400g','Membrillo en almibar listo para servir.',                    48.00, '/static/img/almibar_membrillo.jpg',1);

INSERT INTO sucursal (id, nombre, direccion, telefono) VALUES
  (1, 'Ciudad de Guatemala',     'Zona 10, Ciudad de Guatemala',          '2222-1111'),
  (2, 'Quetzaltenango',          'Zona 1, Quetzaltenango',                '7777-2222'),
  (3, 'Mazatenango',             'Centro, Mazatenango, Suchitepequez',    '7888-3333'),
  (4, 'Escuintla',               'Centro, Escuintla',                     '7999-4444'),
  (5, 'Puerto Barrios',          'Centro, Puerto Barrios, Izabal',        '7444-5555'),
  (6, 'Jutiapa',                 'Centro, Jutiapa',                       '7555-6666');

-- Stock por sucursal (existencia inicial 50-200 frascos por combinacion)
INSERT INTO stock_sucursal (producto_id, sucursal_id, existencia) VALUES
  (1,1,180),(1,2,140),(1,3,90),(1,4,75),(1,5,60),(1,6,80),
  (2,1,120),(2,2,100),(2,3,70),(2,4,55),(2,5,50),(2,6,65),
  (3,1,110),(3,2, 95),(3,3,60),(3,4,50),(3,5,45),(3,6,55),
  (4,1,100),(4,2, 85),(4,3,55),(4,4,45),(4,5,40),(4,6,50),
  (5,1, 90),(5,2, 75),(5,3,50),(5,4,40),(5,5,35),(5,6,45),
  (6,1, 70),(6,2, 60),(6,3,40),(6,4,30),(6,5,25),(6,6,35),
  (7,1, 80),(7,2, 65),(7,3,45),(7,4,35),(7,5,30),(7,6,40);

-- Cliente generico para ventas mostrador
INSERT INTO cliente (id, nombre, nit, email, telefono, direccion) VALUES
  (1, 'Consumidor Final', 'CF', NULL, NULL, NULL);
