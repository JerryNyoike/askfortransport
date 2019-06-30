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
    pictures TEXT NOT NULL,
    transporter_id INT(11) NOT NULL,

    PRIMARY KEY(id),
    FOREIGN KEY(transporter_id) REFERENCES transporter(id)
        ON UPDATE CASCADE ON DELETE CASCADE
<<<<<<< HEAD
);
=======
);
>>>>>>> Add sql to create vehicle table and create relationship between vehicle table and transporter table
