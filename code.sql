CREATE DATABASE Healthcare

CREATE TABLE Appointments (
AppointmentID INT,
PatientName VARCHAR(100),
DoctorName VARCHAR(100),
AppointmentTime TIME
);

USE master;
GO

GRANT ALTER ANY LOGIN TO [HealthcareAdmin];


USE Healthcare;
GO

CREATE ROLE Doctor;
CREATE ROLE Customer;

GRANT SELECT, UPDATE, INSERT, DELETE ON Appointments TO Doctor;

GRANT INSERT ON Appointments TO Customer;

USE Healthcare;
GO

CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'Pa$$w0rd';

CREATE TABLE Patient (
Name NVARCHAR(50),
ID int,
Status BIT
);

CREATE TABLE Doctor (
Name VARCHAR(100),
ID int
);

OPEN MASTER KEY DECRYPTION BY PASSWORD = 'Pa$$w0rd';
--Create cert
CREATE CERTIFICATE NameCert WITH SUBJECT = 'Name characters';
GO
--Create symmetry key
CREATE SYMMETRIC KEY NameKey WITH ALGORITHM=AES_256 ENCRYPTION BY CERTIFICATE NameCert;



--Username: HealthAdmin
--Password: Pa$$w0rd

Master key decryption password: Pa$$w0rd
