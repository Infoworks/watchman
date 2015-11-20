CREATE TABLE DRUG (DRUG_ID INTEGER PRIMARY KEY, NDC TEXT, NAME TEXT) ENGINE=InnoDB;
INSERT INTO DRUG VALUES(1318696749,'08456210062','Trulicity');
INSERT INTO DRUG VALUES(1318695159,'05042812051','Quinidine Gluconate');
INSERT INTO DRUG VALUES(1318756680,'99999218881','Strattera');
INSERT INTO DRUG VALUES(1597302634,'99999198270','Symbyax');
INSERT INTO DRUG VALUES(1318851767,'99999904963','Cymbalta');
INSERT INTO DRUG VALUES(1318717099,'99999065470','Evista');
INSERT INTO DRUG VALUES(1318759473,'99999229480','Zyprexa');

CREATE TABLE MEMBERS (MBR_NBR INTEGER PRIMARY KEY, MBR_NAME TEXT, MBR_DOB DATE, MBR_EFF_DT DATE, MBR_EXP_DT DATE, MAIL_BENEFIT TEXT) ENGINE=InnoDB;
INSERT INTO MEMBERS VALUES(1508,'Nancy Davolio','1948-12-08','2015-01-20','2015-07-20','Y');
INSERT INTO MEMBERS VALUES(7687,'Andrew Fuller','1952-02-19','2015-02-10','2016-02-10','Y');
INSERT INTO MEMBERS VALUES(9928,'Janet Leverling','1963-08-30','2015-02-20','2016-02-20','Y');
INSERT INTO MEMBERS VALUES(6333,'Margaret Peacock','1937-09-19','2011-02-10','2016-02-10','Y');
INSERT INTO MEMBERS VALUES(5261,'Steven Buchanan','1955-03-04','2015-02-10','2016-02-10','Y');
INSERT INTO MEMBERS VALUES(1977,'Michael Suyama','1963-07-02','2015-01-30','2016-01-30','Y');
INSERT INTO MEMBERS VALUES(29,'Robert King','1960-05-29','2015-02-20','2015-08-20','Y');
INSERT INTO MEMBERS VALUES(6713,'Laura Callahan','1958-01-09','2015-02-10','2015-08-10','Y');
INSERT INTO MEMBERS VALUES(5543,'Anne Dodsworth','1966-01-27','2015-02-20','2015-08-20','Y');
INSERT INTO MEMBERS VALUES(669,'Peacock Andrew','1955-03-04','2015-01-20','2015-07-20','Y');

CREATE TABLE PRESCRIBER (PRSCBR_ID INTEGER PRIMARY KEY, DEA_NBR BIGINT, LAST_NM TEXT, ST_LIC_NBR BIGINT) ENGINE=InnoDB;
INSERT INTO PRESCRIBER VALUES('30950631','27367290144','Abigail','7365830247');
INSERT INTO PRESCRIBER VALUES('18786065','28155876565','Madison','8156237586');
INSERT INTO PRESCRIBER VALUES('19501205','29009098375','Charlotte','9002348400');
INSERT INTO PRESCRIBER VALUES('18747482','29102517957','Harper','9100029322');
INSERT INTO PRESCRIBER VALUES('18098399','28278839459','Sofia','8276709810');
INSERT INTO PRESCRIBER VALUES('16938606','27664920814','Avery','7662947498');
INSERT INTO PRESCRIBER VALUES('20317075','27442890842','Elizabeth','7435991917');
INSERT INTO PRESCRIBER VALUES('19623359','28450254328','Amelia','8449809592');
INSERT INTO PRESCRIBER VALUES('18449769','29071572566','Evelyn','9065583257');
INSERT INTO PRESCRIBER VALUES('17833569','26733873808','Ella','6735220580');

CREATE TABLE RX_PRESCRIPTION (PRSCRT_ID INTEGER PRIMARY KEY, WRTN_DT INTEGER, DRUG_ID INTEGER, PRSCBR_ID INTEGER, ALLW_REFIL_QTY INTEGER, FOREIGN KEY (DRUG_ID) REFERENCES DRUG (DRUG_ID), FOREIGN KEY (PRSCBR_ID) REFERENCES PRESCRIBER (PRSCBR_ID)) ENGINE=InnoDB;
INSERT INTO RX_PRESCRIPTION VALUES(808049572,'2015-01-25',1318696749,30950631,0);
INSERT INTO RX_PRESCRIPTION VALUES(513129025,'2015-02-11',1318695159,18786065,2);
INSERT INTO RX_PRESCRIPTION VALUES(723461778,'2015-02-28',1318756680,19501205,5);
INSERT INTO RX_PRESCRIPTION VALUES(115960849,'2011-02-10',1597302634,18747482,11);
INSERT INTO RX_PRESCRIPTION VALUES(117042270,'2015-02-12',1318851767,18098399,5);
INSERT INTO RX_PRESCRIPTION VALUES(512279070,'2015-01-31',1318717099,16938606,3);
INSERT INTO RX_PRESCRIPTION VALUES(866753619,'2015-02-25',1318759473,20317075,2);
INSERT INTO RX_PRESCRIPTION VALUES(485991984,'2015-02-16',1318756680,19623359,11);
INSERT INTO RX_PRESCRIPTION VALUES(369085085,'2015-02-24',1597302634,18449769,3);
INSERT INTO RX_PRESCRIPTION VALUES(417840551,'2015-01-27',1318851767,17833569,0);

CREATE TABLE STORE (STORE_ID BIGINT PRIMARY KEY, CHAIN_ID INTEGER, AREA_ID INTEGER, STORE_ST_LIC_NBR BIGINT) ENGINE=InnoDB;
INSERT INTO STORE VALUES('7365289195','1480','8582','27365299257');
INSERT INTO STORE VALUES('8155750235','6058','3833','28155760126');
INSERT INTO STORE VALUES('9000975365','5943','1530','29000982838');
INSERT INTO STORE VALUES('9093444366','3760','561','29093448687');
INSERT INTO STORE VALUES('8274023863','1050','8225','28274033138');
INSERT INTO STORE VALUES('7656296497','1541','6318','27656304356');
INSERT INTO STORE VALUES('7435608436','6706','7578','27435622720');
INSERT INTO STORE VALUES('8449208199','4188','5177','28449217564');
INSERT INTO STORE VALUES('9063313835','573','3068','29063317476');
INSERT INTO STORE VALUES('6731316309','8116','8202','26731332627');

CREATE TABLE RX_FILL (PRSCRT_FILL_ID BIGINT PRIMARY KEY, PRSCRT_ID INTEGER, REC_EFF_DT DATE, DAY_SPLY_QTY INTEGER, MBR_NBR INTEGER, STORE_ID BIGINT, MAIL_OR_RETAIL TEXT, FOREIGN KEY (PRSCRT_ID) REFERENCES RX_PRESCRIPTION (PRSCRT_ID), FOREIGN KEY (MBR_NBR) REFERENCES MEMBERS (MBR_NBR), FOREIGN KEY (STORE_ID) REFERENCES STORE (STORE_ID)) ENGINE=InnoDB;
INSERT INTO RX_FILL VALUES('26731316309','417840551','2015-01-27','90','669','7365289195','R');
INSERT INTO RX_FILL VALUES('27212717883','512279070','2015-01-31','30','1977','8155750235','R');
INSERT INTO RX_FILL VALUES('27365289195','808049572','2015-01-25','90','1508','9000975365','R');
INSERT INTO RX_FILL VALUES('27365610266','485991984','2015-03-16','30','6713','9093444366','M');
INSERT INTO RX_FILL VALUES('27367125142','369085085','2015-03-29','30','5543','8274023863','R');
INSERT INTO RX_FILL VALUES('27405044556','117042270','2015-03-12','30','5261','7656296497','R');
INSERT INTO RX_FILL VALUES('27435608436','866753619','2015-02-25','30','29','7435608436','R');
INSERT INTO RX_FILL VALUES('27491263837','417840551','2015-02-27','90','669','8449208199','R');
INSERT INTO RX_FILL VALUES('27548951906','808049572','2015-03-25','90','1508','9063313835','R');
INSERT INTO RX_FILL VALUES('27550107884','513129025','2015-04-11','30','7687','6731316309','R');
INSERT INTO RX_FILL VALUES('27615784167','513129025','2015-03-11','30','7687','7365289195','R');
INSERT INTO RX_FILL VALUES('27655539732','723461778','2015-04-28','30','9928','8155750235','R');
INSERT INTO RX_FILL VALUES('27655824852','115960849','2011-04-10','30','6333','9000975365','M');
INSERT INTO RX_FILL VALUES('27656296497','512279070','2015-01-31','30','1977','9093444366','R');
INSERT INTO RX_FILL VALUES('27656735882','117042270','2015-04-12','30','5261','8274023863','R');
INSERT INTO RX_FILL VALUES('27714056468','512279070','2015-03-31','30','1977','7656296497','R');
INSERT INTO RX_FILL VALUES('27823246998','866753619','2015-04-25','30','29','7435608436','R');
INSERT INTO RX_FILL VALUES('27943510165','485991984','2015-04-16','30','6713','8449208199','M');
INSERT INTO RX_FILL VALUES('27995822186','369085085','2015-04-29','30','5543','9063313835','R');
INSERT INTO RX_FILL VALUES('28006956590','417840551','2015-03-27','90','669','6731316309','R');
INSERT INTO RX_FILL VALUES('28036739765','808049572','2015-04-25','90','1508','7365289195','M');
INSERT INTO RX_FILL VALUES('28155750235','513129025','2015-02-11','30','7687','8155750235','R');
INSERT INTO RX_FILL VALUES('28221745448','513129025','2015-05-11','30','7687','9000975365','R');
INSERT INTO RX_FILL VALUES('28222570628','723461778','2015-05-28','30','9928','9093444366','R');
INSERT INTO RX_FILL VALUES('28222596383','115960849','2011-05-10','30','6333','8274023863','M');
INSERT INTO RX_FILL VALUES('28272966745','117042270','2015-05-12','30','5261','7656296497','R');
INSERT INTO RX_FILL VALUES('28274023863','117042270','2015-02-12','30','5261','7435608436','R');
INSERT INTO RX_FILL VALUES('28449208199','485991984','2015-02-16','30','6713','8449208199','M');
INSERT INTO RX_FILL VALUES('28569308985','512279070','2015-04-30','30','1977','9063313835','M');
INSERT INTO RX_FILL VALUES('28615011103','866753619','2015-05-25','30','29','6731316309','R');
INSERT INTO RX_FILL VALUES('28669728108','485991984','2015-05-16','30','6713','7365289195','M');
INSERT INTO RX_FILL VALUES('28725150633','866753619','2015-03-25','30','29','8155750235','R');
INSERT INTO RX_FILL VALUES('28978295333','369085085','2015-05-29','30','5543','9000975365','R');
INSERT INTO RX_FILL VALUES('29000633698','417840551','2015-04-27','90','669','9093444366','R');
INSERT INTO RX_FILL VALUES('29000975365','723461778','2015-02-28','30','9928','8274023863','R');
INSERT INTO RX_FILL VALUES('29062145316','808049572','2015-02-25','90','1508','7656296497','R');
INSERT INTO RX_FILL VALUES('29063313835','369085085','2015-03-29','30','5543','7435608436','R');
INSERT INTO RX_FILL VALUES('29093444366','115960849','2011-02-10','30','6333','8449208199','M');
INSERT INTO RX_FILL VALUES('29163430199','115960849','2011-03-10','30','6333','9063313835','M');
INSERT INTO RX_FILL VALUES('29419710689','723461778','2015-03-28','30','9928','6731316309','R');
