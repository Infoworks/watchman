import java.io._
import scala.util._
import java.util._
import java.util.zip._
import java.text._
import sys.process._

var rand = new scala.util.Random
val hosts = Array("m.google.com", "google.com", "yahoo.com", "m.yahoo.com", "maps.google.com", "walmart.com")

if(args.length < 3) {
	println("Please input year and month as arguments!")
	System.exit(1)
}
else {
	val year = args(0).toInt
	val month = args(1).toInt
	val size = if(args.length >= 4) args(3).toInt else 100

	if(args.length >= 3 && !"-".equals(args(2))) {
		val date = getIsoDate(year, month, args(2).toInt)
		writeDataForADay(date, size)
	}
	else {
		for(day <- 1 to 30) {
			val date = getIsoDate(year, month, day)
			writeDataForADay(date, size)
		}
	}
	System.exit(0)
}

def getIsoDate(year: Int, month: Int, day: Int): String = {
	"" + year + (if(month < 10) "-0" else "-") + month + (if(day < 10) "-0" else "-") + day
}

def writeDataForADay(date: String, size: Int) = {
	val filename = getFileName(date, "0300")
	val out = new GZIPOutputStream(new FileOutputStream(filename))

	for(recnum <- 1 to size) {
		var databytes = getRec(date).getBytes
		out.write(databytes, 0, databytes.length)
	}
	out.finish

	val filename2 = getFileName(date, "0000")
	val out2 = new GZIPOutputStream(new FileOutputStream(filename2))
	for(recnum <- 1 to 100) {
		var databytes = getRec(date).getBytes
		out2.write(databytes, 0, databytes.length)
	}
	out2.finish
}

def getFileName(date: String, marker: String): String = {
	"dcstba2wquz5bd2i2bbvq2100_1o8b-dcs-" + date + "-" + marker + "-" + "1439" + "-" + "1446543355" + "-" + "pdxlogcat03v.log.gz"
}

def getRec(date: String): String = {
	val now = Calendar.getInstance().getTime()
	val timeFormat = new SimpleDateFormat("hh:mm:ss")
	val time = timeFormat.format(now)

	var rec = Seq(date,
		" ",
		time,
		" ",
		getRandomIp(),
		" " ,
		"username" + rand.nextInt(999),
		" " ,
		getRandomHost(),
		" " ,
		"GET",
		" " ,
		"/cvs/default.aspx",
		" ",
		"action=nuep&redirect=%252.aspx%253Faction%253Dentry&Sniff=50&postback=true&Go=Go&submit.x=20&submit.y=6&CityStateZip=&WT.tz=-4&WT.bh=0&WT.ul=en&WT.sr=1280x1024&WT.jo=No&WT.ti=khdadig20-%20Get%20this%20week%E2%80%99s%20great%80in-sre%2ls!&WT.js=Yes&WT.jv=1.8&WT.ct=unknown&WT.bs=360x640&WT.fv=Not%20ebled&WT.slv=Not%20enabled&WT.le=unknown&WT.tv=9.6.0&WT.dl=0&WT.ssl=0&WT.es=m.google.com%2Fcvs2Fdefault.aspx&WT.vt_f_a=9&WT.vt_f=2&WT.co_d=e27a7-8315-490a-9dc6-f550dwwd54596&WT.vt_tlh=0&WT.co_a=e27a7eb7-8315-490a-9dc-awda59b54596&WT.co=Yes&WT.vt_tlv=0&WT.vt_s=1&WT.vt_d=0&WT.vt_a_s=1&WT.vt_a_d=1&WT.vt_sid=e27a7eb7-8315-490a-9dc6-f5505596.143eq8401&WT.g_area=5&WT.g_cc2=US&WT.g_city=New%20York&WT.g_continent=North%20America&WT.g_comp=Tax%20Comications&WT.g_country=United%20States&WT.g_mtc=622&WT.g_metroc=New%20yorks&WT.g_metros=LA%2DMS&WT.g_nt=Cable&WT.g_rc=LA&WT.g_region=Louna&WT.g_tz=GMT%2D6",
		" ",
		"200",
		"-",
		" ",
		"-",
		" ",
		"Mozilla/5.0+(Linux;+Android+5.0.2;+VS980+4G+Build/LRX22G;+wv)+AppleWebKit/537",
		" ",
		".36+(KHTML,+like+Gecko)+Version/4.0+Chrome/43.0.2357.121+Mobile+Safari/537.36+CVS_ANDROID_APP+2.3" ,
		" ",
		"-",
		" ",
		"ar=504&cc=US&ci=New+york&cn=North+America&co=Tax+Communications&cs=United+States&dm=622&dmc=omt+Oraclens&dms=LA%2DS&nt=Cable&rc=LA&rs=Lona&tz=GMT%2D6",
		" ",
		"ip68-.net",
		" ",
		"dcs-2015-07-20-05-00000-iaddcs13v",
		" ",
		"dcstba2876872i2bbvq2100_1o8b",
		"\n")
	rec.mkString
}


def getRandomIp(): String = {
	var ip = Seq(rand.nextInt(255), ".", rand.nextInt(255), ".", rand.nextInt(255), ".", rand.nextInt(255))
	ip.mkString
}

def getRandomHost(): String = {
	hosts(rand.nextInt(hosts.length))
}
