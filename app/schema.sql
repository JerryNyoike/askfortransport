CREATE TABLE user(
    id INT(11) NOT NULL AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    phone INT(20) NOT NULL,
    pwd VARCHAR(50) NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE transporter(
    id INT(11) NOT NULL AUTO_INCREMENT,
    email VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    dl_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(20) NOT NULL,
    phone INT(20) NOT NULL,
    pwd VARCHAR(50) NOT NULL,

    PRIMARY KEY(id)
);

CREATE TABLE vehicle(
    id INT(11) NOT NULL AUTO_INCREMENT,
    capacity INT(11) NOT NULL,
    price INT(11) NOT NULL,
    number_plate INT(11) NOT NULL,
    pictures VARCHAR(100) NOT NULL DEFAULT 'No images',
    transporter_id INT(11) NOT NULL,
    booked VARCHAR(10) NOT NULL DEFAULT 'no',

    PRIMARY KEY(id),
    FOREIGN KEY(transporter_id) REFERENCES transporter(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);
