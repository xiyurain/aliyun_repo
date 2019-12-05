USE test0;
CREATE TABLE file_info
(
	file_id 	int			NOT NULL AUTO_INCREMENT,
    file_name	char(100)	NOT NULL,
    file_size	float		NULL,
    uploader	char(50)	NOT NULL,
    sharetime	char(50)	NOT NULL,
    PRIMARY KEY	(file_id)
)ENGINE=InnoDB;
