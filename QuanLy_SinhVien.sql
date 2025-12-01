create database QuanLy_SinhVien;
use QuanLy_SinhVien;

create table KHOA (
makhoa char(10) primary key,
tenkhoa nvarchar(100)
);

create table LOP (
malop char(10) primary key,
tenlop nvarchar(50),
khoahoc varchar(10),
siso  int
);

create table SINHVIEN (
maSV char(10) primary key,
hotenSV nvarchar(100),
ngaysinh date,
gioitinh nvarchar(5),
diachi nvarchar(255),
cccd varchar(15) unique,
sdt_canhan varchar(15),
sdt_ngthan varchar(15),
email varchar(100) unique,
trangthai nvarchar(50),
malop char(10),
makhoa char(10),
foreign key (malop) references LOP(malop),
foreign key (makhoa) references KHOA(makhoa)
);

insert into KHOA (makhoa, tenkhoa) values ('MK0025', N'Công nghệ thông tin'), ('MK0016', N'Ngoại Ngữ'), ('MK0038', N'Nông nghiệp');
insert into LOP (malop, tenlop, khoahoc, siso) values ('DH24TH1', N'Tin học 1', '2025', 75), ('DH23NN2', N'Nông Nghiệp 2', '2025', 70), ('DH22TA3', N'Tiếng Anh 3', '2025', 68);
insert into SINHVIEN (maSV, hotenSV, ngaysinh, gioitinh, diachi, cccd, sdt_canhan, sdt_ngthan,email, trangthai, malop, makhoa) values
('DTH234666', N'Phạm Nguyên Anh', '2005-01-02', N'Nữ', N'Long Xuyên', '089303849336', '0823567728', '0825433571', 'phamnguyenanh@gamil.com', N'Đang học', 'DH24TH1','MK0025'),
('DTH234159', N'Trần Kiến An', '2005-03-17', N'Nam', N'Châu Đốc', '089250362583', '0976254331', '0759610252', 'trankienan@gamil.com', N'Đang học', 'DH24TH1','MK0025'),
('DTH225730', N'Dương Hoài Trúc', '2004-02-13', N'Nữ', N'An Phú', '089327098351', '0327988035', '0691734522', 'duonghoaitruc@gamil.com', N'Đang học', 'DH23NN2','MK0038'),
('DTH225589', N'Lâm Vĩnh Hà', '2004-07-20', N'Nam', N'Châu Thành', '089235372873', '0965727159', '0749383251', 'lamvinhha@gamil.com', N'Đã bảo lưu', 'DH23NN2','MK0038'),
('DTH215432', N'Phan Khánh Hoàn', '2003-04-15', N'Nam', N'Tri Tôn', '089225465277', '0361759805', '0537962757', 'phankhanhhoan@gamil.com', N'Đã tốt nghiệp', 'DH22TA3','MK0016'),
('DTH215873', N'Lê Nhã Uyên', '2003-08-26', N'Nữ', N'Châu Phú', '089307685257', '0429680451', '0836795443', 'lenhauyen@gamil.com', N'Đã tốt nghiệp', 'DH22TA3','MK0016');

select * from SINHVIEN
select * from KHOA
select * from LOP