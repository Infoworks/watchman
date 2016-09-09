delete from t_rec_hist where prcs_gid=998877 and rec_hist_gid in(111,112,113,114,115,116);
delete from cat_two_demo;

insert into CAT_TWO_DEMO values ('Test1','Test1','Testing1','CALIFORNIA',111,'2015-11-01','2999-12-31');
insert into T_REC_HIST values(111,998877,'2015-11-01 16:50:00');

insert into CAT_TWO_DEMO values ('Test2','Test2','Testing2','SFO',112,'2015-11-02','2999-12-31');
insert into T_REC_HIST values(112,998877,'2015-11-02 16:50:00');

delete from cat_two_scd1_both;
delete from t_rec_hist where prcs_gid=998877 and rec_hist_gid in(2111,2112,2113,2114,2115,2116,2117,2118,2119,2120,2121,2122,2123,2124,2125);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test1','Test1','Testing1','BOSTON',2111,2111);
insert into T_REC_HIST values(2111,998877,current_timestamp);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test2','Test2','Testing2','CA',2112,2112);
insert into T_REC_HIST values(2112,998877,current_timestamp);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test3','Test3','Testing3','DALLAS',2113,2113);
insert into T_REC_HIST values(2113,998877,current_timestamp);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test4','Test4','Testing4','San Jose',2114,2114);
insert into T_REC_HIST values(2114,998877,current_timestamp);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test5','Test5','Testing5','SFO',2115,2115);
insert into T_REC_HIST values(2115,998877,current_timestamp);


delete from cat_one_demo; 


insert into CAT_ONE_DEMO values ('Test1','Test1','Testing1','SFO','2015-12-14 03:10:40','2015-12-14 03:10:40');
insert into CAT_ONE_DEMO values ('Test2','Test2','Testing2','SFO','2015-12-14 03:11:40','2015-12-14 03:11:40');
insert into CAT_ONE_DEMO values ('Test3','Test3','Testing3','SFO','2016-01-05 03:27:40','2016-01-05 03:27:40');

insert into CAT_ONE_DEMO values ('Test4','Test4','DevTesting4','SFO','2016-01-05 03:27:40','2016-01-05 03:28:40');


insert into CAT_ONE_DEMO values ('Test11','Tet11','Testing11','CA','2015-12-14 03:10:40','2015-12-14 03:10:40');
insert into CAT_ONE_DEMO values ('Test21','Test21','Testing21','CA','2015-12-14 03:11:40','2015-12-14 03:11:40');
insert into CAT_ONE_DEMO values ('Test31','Test31','Testing31','CA','2016-01-05 03:27:40','2016-01-05 03:27:40');

insert into CAT_ONE_DEMO values ('Test41','Test41','DevTesting41','CA','2016-01-05 03:27:40','2016-01-05 03:28:40');


insert into CAT_ONE_DEMO values ('Test111','Test111','Testing111','DALLAS','2015-12-14 03:10:40','2015-12-14 03:10:40');
insert into CAT_ONE_DEMO values ('Test211','Test211','Testing211','DALLAS','2015-12-14 03:11:40','2015-12-14 03:11:40');
insert into CAT_ONE_DEMO values ('Test311','Test311','Testing311','DALLAS','2016-01-05 03:27:40','2016-01-05 03:27:40');

insert into CAT_ONE_DEMO values ('Test411','Test411','DevTesting411','DALLAS','2016-01-05 03:27:40','2016-01-05 03:28:40');



insert into CAT_ONE_DEMO values ('Test1111','Test1111','DevTesting1111','SAN JOSE','2016-03-15 03:10:40','2016-03-15 03:10:40');
insert into CAT_ONE_DEMO values ('Test2111','Test2111','DevTesting2111','SAN JOSE','2016-03-15 03:10:40','2016-03-15 03:10:40');

insert into CAT_ONE_DEMO values ('Test3111','Test3111','TestDevTesting3111','SANJOSE','2016-03-15 03:10:40','2016-03-15 03:10:40');
insert into CAT_ONE_DEMO values ('Test4111','Test4111','DevTesting4111','SAN JOSE','2016-03-15 03:10:40','2016-03-14 05:10:40');

