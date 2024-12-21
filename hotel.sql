-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Dec 21, 2024 at 05:40 AM
-- Server version: 8.0.30
-- PHP Version: 8.3.13

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hotel`
--

-- --------------------------------------------------------

--
-- Table structure for table `mscustomer`
--

CREATE TABLE `mscustomer` (
  `NIK` varchar(20) NOT NULL,
  `nama_customer` varchar(255) NOT NULL,
  `tipe_member` enum('NoMember','Silver','Gold') NOT NULL DEFAULT 'NoMember'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mskamar`
--

CREATE TABLE `mskamar` (
  `Kode_Kamar` char(4) NOT NULL,
  `Kategori` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `mspetugas`
--

CREATE TABLE `mspetugas` (
  `ID_Petugas` int NOT NULL,
  `Nama_Petugas` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `trbooking`
--

CREATE TABLE `trbooking` (
  `ID_Booking` int NOT NULL,
  `NIK` varchar(20) NOT NULL,
  `ID_Petugas` int NOT NULL,
  `Kode_Kamar` char(4) NOT NULL,
  `Waktu_Checkin` datetime NOT NULL,
  `Durasi_Hari` int NOT NULL,
  `Waktu_Checkout` datetime NOT NULL,
  `HargaBayarAwal` int NOT NULL,
  `Denda` int NOT NULL,
  `HargaFinal` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `mscustomer`
--
ALTER TABLE `mscustomer`
  ADD PRIMARY KEY (`NIK`);

--
-- Indexes for table `mskamar`
--
ALTER TABLE `mskamar`
  ADD PRIMARY KEY (`Kode_Kamar`);

--
-- Indexes for table `mspetugas`
--
ALTER TABLE `mspetugas`
  ADD PRIMARY KEY (`ID_Petugas`);

--
-- Indexes for table `trbooking`
--
ALTER TABLE `trbooking`
  ADD PRIMARY KEY (`ID_Booking`),
  ADD KEY `fk_nik` (`NIK`),
  ADD KEY `fk_id_petugas` (`ID_Petugas`),
  ADD KEY `fk_kode_kamar` (`Kode_Kamar`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `trbooking`
--
ALTER TABLE `trbooking`
  ADD CONSTRAINT `fk_id_petugas` FOREIGN KEY (`ID_Petugas`) REFERENCES `mspetugas` (`ID_Petugas`),
  ADD CONSTRAINT `fk_kode_kamar` FOREIGN KEY (`Kode_Kamar`) REFERENCES `mskamar` (`Kode_Kamar`),
  ADD CONSTRAINT `fk_nik` FOREIGN KEY (`NIK`) REFERENCES `mscustomer` (`NIK`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
