CREATE TABLE DEGREE (
    degree_id INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    level     VARCHAR(10)  NOT NULL, -- ENUM instead?
    UNIQUE KEY uq_degree_name_level (name, level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE COURSE (
    course_id      INT AUTO_INCREMENT PRIMARY KEY,
    course_number  VARCHAR(16)  NOT NULL,
    name           VARCHAR(200) NOT NULL,
    UNIQUE KEY uq_course_number (course_number),
    UNIQUE KEY uq_course_name   (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE INSTRUCTOR (
    instructor_id CHAR(8) NOT NULL PRIMARY KEY,
    name          VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE SEMESTER (
    year INT NOT NULL,
    term VARCHAR(10) NOT NULL,
    PRIMARY KEY (year, term) -- primary key is a combination of year and term
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE OBJECTIVE (
    objective_id INT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(20)   NOT NULL,
    title        VARCHAR(120)  NOT NULL,
    description  TEXT          NOT NULL,
    UNIQUE KEY uq_objective_code  (code),
    UNIQUE KEY uq_objective_title (title) -- potentially remove unique title to avoid catching very similiar titles
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE DEGREE_COURSE (
    degree_id INT NOT NULL,
    course_id INT NOT NULL,
    is_core   TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (degree_id, course_id),
    CONSTRAINT fk_degcourse_degree
        FOREIGN KEY (degree_id) REFERENCES DEGREE(degree_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_degcourse_course
        FOREIGN KEY (course_id) REFERENCES COURSE(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE DEGREE_OBJECTIVE (
    degree_id    INT NOT NULL,
    objective_id INT NOT NULL,
    PRIMARY KEY (degree_id, objective_id),
    CONSTRAINT fk_degobj_degree
        FOREIGN KEY (degree_id) REFERENCES DEGREE(degree_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_degobj_objective
        FOREIGN KEY (objective_id) REFERENCES OBJECTIVE(objective_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE SECTION (
    section_id       INT AUTO_INCREMENT PRIMARY KEY,
    course_id        INT NOT NULL,
    year             INT NOT NULL,
    term             VARCHAR(10) NOT NULL,
    instructor_id    CHAR(8) NOT NULL,
    section_number   INT NOT NULL, -- or section_number SMALLINT UNSIGNED CHECK (section_number BETWEEN 1 AND 999)
    enrollment_count INT UNSIGNED NOT NULL DEFAULT 0,
    UNIQUE KEY uq_section (course_id, year, term, section_number),
    CONSTRAINT fk_section_course
        FOREIGN KEY (course_id) REFERENCES COURSE(course_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_section_semester
        FOREIGN KEY (year, term) REFERENCES SEMESTER(year, term) -- using year and term as foreign key
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_section_instructor
        FOREIGN KEY (instructor_id) REFERENCES INSTRUCTOR(instructor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE COURSE_OBJECTIVE (
    degree_id    INT NOT NULL,
    course_id    INT NOT NULL,
    objective_id INT NOT NULL,
    PRIMARY KEY (degree_id, course_id, objective_id),
    CONSTRAINT fk_courseobj_degcourse
        FOREIGN KEY (degree_id, course_id)
        REFERENCES DEGREE_COURSE(degree_id, course_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_courseobj_degobj
        FOREIGN KEY (degree_id, objective_id)
        REFERENCES DEGREE_OBJECTIVE(degree_id, objective_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE EVALUATION (
    section_id   INT NOT NULL,
    degree_id    INT NOT NULL,
    objective_id INT NOT NULL,
    -- course_id     INT NOT NULL,  
    eval_method  VARCHAR(50) NOT NULL,
    count_A      INT UNSIGNED NOT NULL DEFAULT 0,
    count_B      INT UNSIGNED NOT NULL DEFAULT 0,
    count_C      INT UNSIGNED NOT NULL DEFAULT 0,
    count_F      INT UNSIGNED NOT NULL DEFAULT 0,
    improvement_text TEXT NULL,
    PRIMARY KEY (section_id, degree_id, objective_id),
    CONSTRAINT fk_eval_section
        FOREIGN KEY (section_id) REFERENCES SECTION(section_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_eval_degree
        FOREIGN KEY (degree_id) REFERENCES DEGREE(degree_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_eval_objective
        FOREIGN KEY (degree_id, objective_id) REFERENCES DEGREE_OBJECTIVE(degree_id, objective_id)
        ON DELETE CASCADE ON UPDATE CASCADE
   -- CONSTRAINT fk_eval_course
   --    FOREIGN KEY (course_id)
   --     REFERENCES COURSE(course_id)
   --     ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
