DROP DATABASE IF EXISTS mysql_boundary;
CREATE DATABASE IF NOT EXISTS mysql_boundary;
USE mysql_boundary;

CREATE TABLE `root_table` (
	`col_pk`	INTEGER PRIMARY KEY,
	`col_dummy`	INTEGER
);
INSERT INTO root_table VALUES (1,1);
INSERT INTO root_table VALUES (2,2);
INSERT INTO root_table VALUES (3,3);
INSERT INTO root_table VALUES (4,4);
INSERT INTO root_table VALUES (5,5);
INSERT INTO root_table VALUES (6,6);

CREATE TABLE `test_datatype_numeric` (
	`col_pk`	INTEGER PRIMARY KEY,
	`col_integer`	INTEGER,
	`col_tinyint`	TINYINT,
	`col_smallint`	SMALLINT,
	`col_mediumint`	MEDIUMINT,
	`col_bigint`	BIGINT,
	`col_float`	FLOAT,
	`col_double`	DOUBLE,
	`col_decimal`	DECIMAL
);
INSERT INTO test_datatype_numeric VALUES (1, -2147483648, -128, -32768, -8388608, -9223372036854775808, -3.402823466E+38, -1.7976931348, 0.0);
INSERT INTO test_datatype_numeric VALUES (2, 2147483647, 127, 32767, 8388607, 9223372036854775807, -1.175494351E-38, -2.22507385850, 999.9);
INSERT INTO test_datatype_numeric VALUES (3, null, null, null, null,null , null, null, null);
INSERT INTO test_datatype_numeric VALUES (4, 100, 25, 30, 35, 40 , 50.75, 80.99, 20.5);
INSERT INTO test_datatype_numeric VALUES (5, 56, 20, 50, 30, 50 , 100.35, 150.99, 120.5);
INSERT INTO test_datatype_numeric VALUES (6, 51, 15, 5, 60, 90 , 15.15, 14.99, 130.5);

CREATE TABLE `test_datatype_string` (
	`col_pk`	INTEGER PRIMARY KEY,
	`col_char`	CHAR(10),
	`col_varchar`	VARCHAR(10),
	`col_tinytext`	TINYTEXT,
	`col_text`	TEXT,
	`col_mediumtext` MEDIUMTEXT,
	`col_longtext`	LONGTEXT
);
INSERT INTO test_datatype_string VALUES (1, 'dt_char', 'dt_varchar', 'dt_tinytext', 'dt_text012345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061626364656667686970717273747576777879808182838485868788899091929394959697989912345678900123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899123456789001234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283848586878889909192939495969798991234567890012345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061626364656667686970717273747576777879808182838485868788899091929394959697989912345678900123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899123456789001234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283848586878889909192939495969798991234567890012345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061626364656667686970717273747576777879808182838485868788899091929394959697989912345678900123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899123456789001234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283848586878889909192939495969798991234567890012345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061626364656667686970717273747576777879808182838485868788899091929394959697989912345678900', 'dt_mediumtext', 'dt_longtext');
INSERT INTO test_datatype_string VALUES (2, null, null, null, null, null, null );
INSERT INTO test_datatype_string VALUES (3, '', '', '', '', '', '' );

CREATE TABLE `test_datatype_binary` (	
	`col_pk`	INTEGER PRIMARY KEY,
	`col_tinyblob`	TINYBLOB,
	`col_blob`	BLOB,
	`col_mediumblob`	MEDIUMBLOB,
	`col_longblob`	LONGBLOB,
	`col_binary`	BINARY(5),
	`col_varbinary`	VARBINARY(5)
);
INSERT INTO test_datatype_binary VALUES (1, 'FFD8FFE', 'FFD8FFE0', 'FFD8FFE00', 'FFD8FFE000104A464946', 'FFD8FFE2', 'FFD8FFE1');
INSERT INTO test_datatype_binary VALUES (2, null, null, null, null, null, null);
INSERT INTO test_datatype_binary VALUES (3, '', '', '', '', '', '');

CREATE TABLE `test_datatype_datetime` (	
	`col_pk`	INTEGER PRIMARY KEY,
	`col_date`	DATE,
	`col_datetime`	DATETIME,
	`col_time`	TIME,
	`col_timestamp`	TIMESTAMP,
	`col_year`	YEAR
);
INSERT INTO test_datatype_datetime VALUES (1, '2015-12-31', '2015-12-31 23:59:59', '12:59:59', '2018-01-19 03:14:07', '2155');
INSERT INTO test_datatype_datetime VALUES (2, '2015-01-01', '2015-01-01 00:00:00', '04:59:59', '1970-01-01 00:00:01', '1901');
INSERT INTO test_datatype_datetime VALUES (3, null, null, null, null, null);

CREATE TABLE `test_datatype_misc` (
	`col_pk`	INTEGER PRIMARY KEY,
	`col_bit` BIT,
	`col_enum` ENUM('tiny', 'medium', 'big')
);
INSERT INTO test_datatype_misc VALUES (1, true, 'tiny');
INSERT INTO test_datatype_misc VALUES (2, null, null);

CREATE TABLE `test_charset_specialchar` (
	`col_pk`	INTEGER PRIMARY KEY,
	`col_char_big5`	CHAR(10) CHARACTER SET big5,
	`col_char_dec8`	CHAR(10) CHARACTER SET dec8,
	`col_char_cp850`	CHAR(10) CHARACTER SET cp850,
	`col_char_hp8`	CHAR(10) CHARACTER SET hp8,
	`col_char_koi8r`	CHAR(10) CHARACTER SET koi8r,
	`col_char_latin1`	CHAR(10) CHARACTER SET latin1,
	`col_char_latin2`	CHAR(10) CHARACTER SET latin2,
	`col_char_swe7`	CHAR(10) CHARACTER SET swe7,
	`col_char_ascii`	CHAR(10) CHARACTER SET ascii,
	`col_char_sjis`	CHAR(10) CHARACTER SET sjis,
	`col_char_hebrew`	CHAR(10) CHARACTER SET hebrew,
	`col_char_tis620`	CHAR(10) CHARACTER SET tis620,
	`col_char_euckr`	CHAR(10) CHARACTER SET euckr,
	`col_char_koi8u`	CHAR(10) CHARACTER SET koi8u,
	`col_char_gb2312`	CHAR(10) CHARACTER SET gb2312,
	`col_char_greek`	CHAR(10) CHARACTER SET greek,
	`col_char_cp1250`	CHAR(10) CHARACTER SET cp1250,
	`col_char_gbk`	CHAR(10) CHARACTER SET gbk,
	`col_char_latin5`	CHAR(10) CHARACTER SET latin5,
	`col_char_armscii8`	CHAR(10) CHARACTER SET armscii8,
	`col_char_utf8`	CHAR(10) CHARACTER SET utf8,
	`col_char_ucs2`	CHAR(10) CHARACTER SET ucs2,
	`col_char_cp866`	CHAR(10) CHARACTER SET cp866,
	`col_char_keybcs2`	CHAR(10) CHARACTER SET keybcs2,
	`col_char_macce`	CHAR(10) CHARACTER SET macce,
	`col_char_macroman`	CHAR(10) CHARACTER SET macroman,
	`col_char_cp852`	CHAR(10) CHARACTER SET cp852,
	`col_char_latin7`	CHAR(10) CHARACTER SET latin7,
	`col_char_cp1251`	CHAR(10) CHARACTER SET cp1251,
	`col_char_cp1256`	CHAR(10) CHARACTER SET cp1256,
	`col_char_cp1257`	CHAR(10) CHARACTER SET cp1257,
	`col_char_binary`	CHAR(10) CHARACTER SET binary
);
INSERT INTO test_charset_specialchar VALUES (1, 'big5', 'dec8', 'cp850', 'hp8', 'koi8r', 'latin1', 'latin2', 'swe7', 'ascii', 'sjis', 'hebrew', 'tis620', 'euckr', 'koi8u', 'gb2312', 'greek', 'cp1250', 'gbk', 'latin5', 'armscii8', 'utf8', 'ucs2', 'cp866', 'keybcs2', 'macce', 'macroman', 'cp852', 'latin7', 'cp1251', 'cp1256', 'cp1257', 'cpbin');
INSERT INTO test_charset_specialchar VALUES (2, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null);
INSERT INTO test_charset_specialchar VALUES (3, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');
INSERT INTO test_charset_specialchar VALUES (4, '\0big5', 'd\'ec8', 'cp850\"', 'h\bp8', 'koi\n8r', 'lat\rin1', '\tlatin2', 'swe7\z', 'asc\\ii', 'sj\%is', 'hebr\_ew', 'tis62\00', 'euc\'kr', 'ko\"i8u', '\bgb2312', 'g\nreek', 'cp1250\r', 'g\tbk', 'latin\z5', 'arms\\cii8', 'u\%tf8', 'u\_cs2', 'cp8\066', 'keyb\'cs2', 'ma\"cce', 'macro\bman', 'cp\n852', 'lat\rin7', 'cp1251\z', 'cp12\%56', 'cp1\_257', 'cp1\_257');

CREATE VIEW data_view AS SELECT col_integer, col_tinyint, col_smallint, col_mediumint, col_bigint, col_float, col_double, col_decimal, col_char, col_varchar, col_tinytext, col_text, col_mediumtext, col_longtext, col_date, col_datetime, col_time, col_timestamp, col_year FROM test_datatype_string, test_datatype_numeric, test_datatype_datetime;

