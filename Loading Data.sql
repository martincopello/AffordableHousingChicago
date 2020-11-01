create database finalproj;
use finalproj;
CREATE TABLE `closest_park` (
  `index` int(11) UNSIGNED ,
  `Address` text,
  `Latitude` double DEFAULT NULL,
  `Longitude` double DEFAULT NULL,
  `name` text,
  `pdists` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#must move into this directory
SHOW VARIABLES LIKE "secure_file_priv";
SELECT @@global.secure_file_priv;
SET @@SQL_MODE = '';

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/closest_park.csv' INTO TABLE closest_park
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

#close bus, and l and bus routes did with the wizard
CREATE TABLE `closest_l_bus` (
  `MyUnknownColumn` int(11),
  `index` int(11) UNSIGNED,
  `Address` text,
  `Lat` double DEFAULT NULL,
  `Long` double DEFAULT NULL,
  `Bus_Distance` double DEFAULT NULL,
  `Bus_Stop` text,
  `L_Distance` double DEFAULT NULL,
  `L_Stop` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/Closest_L_Bus.csv' INTO TABLE closest_l_bus
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

#Close L Lines
CREATE TABLE `close_l_lines` (
  `index` int(11) UNSIGNED,
  `Address` text,
  `Latitude` double DEFAULT NULL,
  `Longitude` double DEFAULT NULL,
  `place_name` text,
  `longname` text,
  `lines` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/Close_L_Lines.csv' INTO TABLE close_l_lines
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 ROWS;


#bus
CREATE TABLE `close_bus_routes` (
	`index` int(11) UNSIGNED, 
    `Address` text, 
    `Latitude` double, 
    `Longitude` double, 
    `public_name` text, 
    `routes` text, 
    `owlroutes` text
)  ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/Close_Bus_Routes.csv' INTO TABLE close_bus_routes
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 ROWS;

#general
CREATE TABLE `developments` 
	(`index` int(11) UNSIGNED, 
    `Community Area Name` varchar(250), 
    `Community Area Number` int, 
    `Property Type` text, 
    `Property Name` text, 
    `Address` text, 
    `Zip Code` int, 
    `Phone Number` text, 
    `Management Company` text, 
    `Units` int, 
    `X Coordinate` text, 
    `Y Coordinate` text, 
    `Latitude` double, 
    `Longitude` double, 
    `Location` text, 
    `vtouse` text, 
    `Walkscore` int, 
    `Bikescore` int, 
    `Transitscore` int
)  ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/Developments, with scores.csv' INTO TABLE developments
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 ROWS;
#fix the messed up spelling of garfield park, diff spelling of lakeview
update developments 
set `community area name` = 'East Garfield Park' where `community area name` = 'East Garfiled Park';
update developments 
set `community area name` = 'Lake View' where `community area name` = 'Lakeview';
#uppercase
update developments 
set `community area name` = upper(`community area name`);
#-----------------------------------------
#----Commerce DDL-------------------------
#-----------------------------------------

#Assumption: database us called 'affordable_housing'
#Affordable Housing Development table is called dim_affordable_housing_development
#and each affordable housing development's primary key is called development_id
#Foreign keys are zip_code and neighborhood from separate table
#consisting of affordable housing development locations
#Primary key is license_id, to represent one business

USE finalproj;
DROP TABLE IF EXISTS `finalproj`.`dim_commerce`;
CREATE TABLE IF NOT EXISTS `finalproj`.`dim_commerce` (
  `license_id` INT(7) NOT NULL,
  `business_name` VARCHAR(64) NOT NULL,
  `zip_code` INT(5) NOT NULL,
  `ward` INT (5) NOT NULL,
  `precinct` INT (5) DEFAULT NULL,
  `license_description` VARCHAR(64) NOT NULL,
  `application_req_completed` VARCHAR(64) NOT NULL,
  `license_start_date` VARCHAR(64) NOT NULL,
  `license_end_date` VARCHAR(64) NOT NULL,
  `date_license_issued` VARCHAR(64) NOT NULL,
  `neighborhood` varchar(250),
  PRIMARY KEY (`license_id`) 
    )
ENGINE = InnoDB
DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#-----------------------------------------
#----Commerce DML-------------------------
#-----------------------------------------
#Assumptions: We are using the 'reduced' version of the commerce dataset.
#Essentially, I removed redundant columns or unnecessary columns.

#I removed: ID (because we already have license ID), Account # (related to
#each business' account with the city), Site Number, Legal Name, Address, City
#State, Zip Code, Ward-Precinct, Police District, License Code, License Number, Application Type,
#Application Created, Conditional Approval, License Expiration Date, 
#License approved for issuance, license_status, License Status Change, 
#Latitude, Longitude, Location

#Remaining columns: License ID, Business Name, License Description, 
#Application Requirements  Completed, License Start Date, License End Date
#Date License Issued, Neighborhood, Zip Code, Ward, Precinct

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/commerce_business_licenses_reduced.csv' 
INTO TABLE dim_commerce
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;


#convert the date rows
SET @@SQL_SAFE_UPDATES = 0;
update `dim_commerce`
set `application_req_completed` =  STR_TO_DATE(`application_req_completed`, '%m/%d/%Y') ;
update `dim_commerce`
set `license_start_date`  =  STR_TO_DATE(`license_start_date` , '%m/%d/%Y') ;
update `dim_commerce`
set `license_end_date` =  STR_TO_DATE(`license_end_date`, '%m/%d/%Y') ;
update `dim_commerce`
set `date_license_issued` =  STR_TO_DATE(`date_license_issued`, '%m/%d/%Y') ;

#property values by CA
#DDL
CREATE TABLE `finalproj`.`property_values` 
(`Neighborhood` varchar(250), 
`Assessed` double)
DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

#DML
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQLServer 8.0/Uploads/df_pvt.csv' 
INTO TABLE property_values
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;


#add a bunch of pks
alter table developments MODIFY COLUMN `index` INT(11) UNSIGNED PRIMARY KEY;
alter table closest_park MODIFY COLUMN `index` INT(11) UNSIGNED PRIMARY KEY;
alter table closest_park ADD CONSTRAINT FK_parkidx FOREIGN KEY (`index`) REFERENCES developments(`index`);

alter table closest_l_bus ADD CONSTRAINT FK_lbus FOREIGN KEY (`index`)  REFERENCES developments(`index`) ;
alter table close_l_lines ADD CONSTRAINT FK_cl FOREIGN KEY (`index`) REFERENCES developments(`index`);
alter table close_bus_routes ADD CONSTRAINT FK_cbus FOREIGN KEY (`index`) REFERENCES developments(`index`);
CREATE INDEX neighborhood_index ON developments (`Community Area Name`);
CREATE INDEX n_ix on dim_commerce (`neighborhood`);
alter table developments ADD CONSTRAINT FK_dev_CA FOREIGN KEY (`community area name`) REFERENCES dim_commerce(`neighborhood`);
alter table property_values ADD CONSTRAINT FK_propvals_CA FOREIGN KEY (`Neighborhood`) REFERENCES dim_commerce(`neighborhood`);

