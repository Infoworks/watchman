CREATE DATABASE IF NOT EXISTS sftp_webtrends;
USE sftp_webtrends;

DROP TABLE webtrend_cvsdotcom_s;
CREATE EXTERNAL TABLE webtrend_cvsdotcom_s (
    date_s                  string,
    time_s                  string,
    c_ip                    string,
    cs_username             string,
    cs_host                 string,
    cs_method               string,
    cs_uri_stem             string,
    cs_uri_query            string,
    c_status                string,
    sc_bytes                string,
    cs_version              string,
    cs_user_agent           string,
    cs_cookie               string,
    cs_referer              string,
    dcs_geo                 string,
    dcs_dns                 string,
    origin_id               string,
    dcs_id                  string
) PARTITIONED BY (monthly_capture string)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ' ' STORED AS TEXTFILE LOCATION '/sqoop/iw/sftp_webtrends';
