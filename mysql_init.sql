# ************************************************************
# Sequel Pro SQL dump
# Version 5438
#
# https://www.sequelpro.com/
# https://github.com/sequelpro/sequelpro
#
# Host: localhost (MySQL 5.6.38)
# Database: reaper
# Generation Time: 2019-06-11 07:47:14 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `crs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `REGISTRATIONNUMBER` varchar(25) DEFAULT NULL,
  `FULLSCIENTIFICNAME` varchar(100) DEFAULT NULL,
  `URL` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `iucn` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `taxonid` int(11) DEFAULT NULL,
  `scientific_name` varchar(100) DEFAULT NULL,
  `kingdom` varchar(20) DEFAULT NULL,
  `phylum` varchar(20) DEFAULT NULL,
  `class` varchar(20) DEFAULT NULL,
  `order` varchar(20) DEFAULT NULL,
  `family` varchar(20) DEFAULT NULL,
  `genus` varchar(20) DEFAULT NULL,
  `main_common_name` varchar(100) DEFAULT NULL,
  `authority` varchar(100) DEFAULT NULL,
  `published_year` varchar(10) DEFAULT NULL,
  `assessment_date` varchar(10) DEFAULT NULL,
  `category` varchar(10) DEFAULT NULL,
  `criteria` varchar(100) DEFAULT NULL,
  `population_trend` varchar(100) DEFAULT NULL,
  `marine_system` tinyint(1) DEFAULT NULL,
  `freshwater_system` tinyint(1) DEFAULT NULL,
  `terrestrial_system` tinyint(1) DEFAULT NULL,
  `assessor` text,
  `reviewer` text,
  `aoo_km2` varchar(25) DEFAULT NULL,
  `eoo_km2` varchar(25) DEFAULT NULL,
  `elevation_upper` varchar(10) DEFAULT NULL,
  `elevation_lower` varchar(10) DEFAULT NULL,
  `depth_upper` varchar(10) DEFAULT NULL,
  `depth_lower` varchar(10) DEFAULT NULL,
  `errata_flag` tinyint(1) DEFAULT NULL,
  `errata_reason` text,
  `amended_flag` tinyint(1) DEFAULT NULL,
  `amended_reason` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `natuurwijzer` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `room` varchar(100) DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `url` varchar(100) DEFAULT NULL,
  `taxon` varchar(1000) DEFAULT NULL,
  `exhibition_rooms` varchar(255) DEFAULT NULL,
  `image_urls` text,
  `author` varchar(100) DEFAULT NULL,
  `intro_text` text,
  `langcode` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tentoonstelling` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Registratienummer` varchar(50) DEFAULT NULL,
  `Zaal` varchar(50) DEFAULT NULL,
  `Zaaldeel` varchar(100) DEFAULT NULL,
  `SCname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `SCname` (`SCname`(100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `topstukken` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `description` text,
  `registrationNumber` varchar(100) DEFAULT NULL,
  `collection` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `scientificName` varchar(100) DEFAULT NULL,
  `year` varchar(10) DEFAULT NULL,
  `expedition` varchar(100) DEFAULT NULL,
  `collector` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `scientificName` (`scientificName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `ttik` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `description` text,
  `classification` text,
  `uninomial` varchar(50) DEFAULT NULL,
  `specific_epithet` varchar(50) DEFAULT NULL,
  `infra_specific_epithet` varchar(50) DEFAULT NULL,
  `authorship` varchar(255) DEFAULT NULL,
  `taxon` varchar(255) DEFAULT NULL,
  `rank` varchar(20) DEFAULT NULL,
  `english` varchar(255) DEFAULT NULL,
  `dutch` varchar(255) DEFAULT NULL,
  `taxon_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `uninomial` (`uninomial`,`specific_epithet`,`infra_specific_epithet`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
