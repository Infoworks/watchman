update CAT_TWO_DEMO set REC_EXPRN_DT='2015-12-04' where FNAME='Test2' and LNAME='Test2' and rec_hist_gid=112;
insert into CAT_TWO_DEMO values ('Test2','Test2','DevTesting2','SFO',113,'2015-12-05','2999-12-31');
insert into T_REC_HIST values(113,998877,'2015-12-05 10:10:10');

insert into CAT_TWO_DEMO values ('Test3','Test3','Testing3','SFO',114,'2015-12-01','2999-12-31');
insert into T_REC_HIST values(114,998877,'2015-12-01 17:50:00');


insert into CAT_TWO_DEMO values ('Test4','Test4','Testing4','SFO',115,'2015-12-06','2999-12-31');
insert into T_REC_HIST values(115,998877,'2015-12-06 17:50:00');

update CAT_TWO_DEMO set REC_EXPRN_DT='2015-12-07' where FNAME='Test1' and LNAME='Test1' and rec_hist_gid=111;
insert into CAT_TWO_DEMO values ('Test1','Test1','DevTesting1','CALIFORNIA',116,'2015-12-08','2999-12-31');
insert into T_REC_HIST values(116,998877,'2015-12-08 17:50:00');



UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2116,PROFESSION='DevTesting1' WHERE FNAME='Test1';
insert into T_REC_HIST values(2116,998877,current_timestamp);


UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2117,PROFESSION='DevTesting4' WHERE FNAME='Test4';
insert into T_REC_HIST values(2117,998877,current_timestamp);


UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2118,PROFESSION='DevTesting2' WHERE FNAME='Test2';
insert into T_REC_HIST values(2118,998877,current_timestamp);

UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2119,PROFESSION='DevTesting3' WHERE FNAME='Test3';
insert into T_REC_HIST values(2119,998877,current_timestamp);


UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2120,PROFESSION='DevTesting5' WHERE FNAME='Test5';
insert into T_REC_HIST values(2120,998877,current_timestamp);


INSERT INTO CAT_TWO_SCD1_BOTH values('Test6','Test6','Testing6','CA',2121,2121);
insert into T_REC_HIST values(2121,998877,current_timestamp);

UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2122,PROFESSION='TestDevTesting6' WHERE FNAME='Test6';
insert into T_REC_HIST values(2122,998877,current_timestamp);

INSERT INTO CAT_TWO_SCD1_BOTH values('Test7','Test7','Testing7','CA',2123,2123);
insert into T_REC_HIST values(2123,998877,current_timestamp);

UPDATE CAT_TWO_SCD1_BOTH SET REC_UPD_HIST_GID=2124,PROFESSION='TestDevTesting7' WHERE FNAME='Test7';
insert into T_REC_HIST values(2124,998877,current_timestamp);


update cat_one_demo set profession='Test41',rec_chg_ts='2016-03-16 03:10:40' where fname='Test41';
update cat_one_demo set profession='Test4',rec_chg_ts='2016-03-16 03:10:40' where fname='Test4';
update cat_one_demo set profession='Test4111',rec_chg_ts='2016-03-16 03:10:40' where fname='Test4111';

update cat_one_demo set profession='Test411',rec_chg_ts='2016-03-17 03:10:40' where fname='Test411';
update cat_one_demo set profession='Prof1',rec_chg_ts='2016-03-17 03:10:40' where fname='Test1';

insert into CAT_ONE_DEMO values ('Test41111','Test41111','DevTesting41111','Dallas','2016-03-17 03:10:40','2016-03-17 03:10:40');
