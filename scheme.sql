create table alerts (
    id int not null primary key auto_increment,
    host varchar(15),
    timestamp_alert varchar(30),
    to_ip varchar(25),
    from_ip varchar(25),
    protocol varchar(10),
    msg varchar(255),
    sid varchar(15),
    rev varchar(10),
    priority int,
    classification varchar(50),
    alert_priority int,
    text_alert varchar(254)
);
