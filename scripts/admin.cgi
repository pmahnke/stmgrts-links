#!/usr/bin/perl

##############################################################
##############################################################
#
# admin.cgi
#  http://stmgrts.org.uk/scripts/admin.cgi?a=list
#  based on ad.cgi script
#  
#  written on 21 Apr 2010 by Peter Mahnke
#  modified
#   - 19 Jul 2010 - added pagination to list of links
#
##############################################################
##############################################################

use CGI::Lite;
use DBI;
require ("/home/stmargarets/cgi-bin/tweeter-v1_1.cgi");

my $dbh = DBI->connect("dbi:Pg:dbname=stmgrtslinks","pmahnke","Shi11t0P",{ RaiseError => 1, AutoCommit => 1    });
my $date      = `date +'%Y-%m-%d'`;
chop($date);
my $thisScript = "/scripts/admin.cgi";
my $msg; 
my $now = "now()";
my @simple_mon = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');

################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {

    # nothing submitted... so PANIC!!!
    &print_page(&password());
    exit;

}

if ($F{'a'} eq "password" && $F{'passwd'} eq "peter") {

	# message for correct Password
	$F{'msg'} = "success";
	$msg .= qq |Correct password &mdash; thank you!|;
 	&print_page(&link_list());
 	exit;
}

if ($F{'passwd'} ne "peter") {

	$F{'msg'} = "error";
	$msg .= qq |Incorrect password!| if ($F{'passwd'} || $F{'a'} eq "password");
    &print_page(&password());
    exit;

} elsif ($F{'a'} eq "delete") {

	# delete Link
	#a=delete&id=7&passwd=D0nk3y
	&deleteLink($F{'id'});
	$F{'msg'} = "notice";
	$msg .= qq |Removed link $F{'id'}!|;
 	&print_page(&link_list());
 	exit;

} elsif ($F{'a'} eq "list" || $F{'a'} eq "link") {

    &print_page(&link_list());

} elsif ($F{'a'} eq "edit") {

    &print_page(&link_edit());

} elsif ($F{'a'} eq "new") {

    &print_page(&link_new());

} elsif ($F{'a'} eq "start") {

    &print_page(&link_new());
    
} elsif ($F{'a'} eq "save" || $F{'a'} eq "link_save" ) {

    &print_page(&link_save());

} elsif ($F{'a'} eq "stat") {

    &print_page(&stats($F{'id'}));

} elsif ($F{'a'} eq "tweet") {

    &print_page(&tweet());
    
} else {
	
	&print_page(&password);
	exit;

}
    
exit;    
        

################################################################################    
sub tweet {

	my $tweet = &make_tweet($F{'tweet'} ,'hi11top');
	$tweet = qq |ERROR| if (!$tweet);
	$msg .= qq |Tweeted: $tweet|;
	return();
	
}

################################################################################    
sub deleteLink {
	
	# remove from tracker_summary table
	my $sql = qq |DELETE FROM tracker_summary WHERE link_id=$F{'id'}|;
	print STDERR $sql;
	$dbh->selectrow_array($sql)if ($dbh->selectrow_array(qq|SELECT link_id FROM tracker_summary WHERE link_id=$F{'id'}|));

	# remove from tracker table
	$sql = qq |DELETE FROM tracker WHERE link_id=$F{'id'}|;
	print STDERR $sql;
	$dbh->selectrow_array($sql)
	    if ($dbh->selectrow_array(qq|SELECT link_id FROM tracker WHERE link_id=$F{'id'}|));

	# remove from link table
	$sql = qq |DELETE FROM links WHERE id=$F{'id'}|;
	print STDERR $sql;
	$dbh->selectrow_array($sql)
		if ($dbh->selectrow_array(qq|SELECT id FROM links WHERE id=$F{'id'}|));;
	
	return();

}

################################################################################    
sub password {

	
    my $out .= qq |
	<fieldset>
	<legend>Password</legend>
	
	<form method="post" action="$thisScript">
	
	<input type="hidden"  name="a" value="password" />
	
	<p><label for="passwd">Password</label><br />$F{'passwd'}  $F{'a'}
    <input type="password"  name="passwd" class="text" /></p>
	
	<p><button type="submit" name="action" value="password"  class="button positive"> <img src="tick.png" alt=""/> Sumbit </button></p>
	
	</form>
	</fieldset>
	|;
    
    return($out);
}

################################################################################    
sub link_list {

	my ($sql, $sth, $out);
	my ($id, $name, $url, $shortcut, $ts, $t);
	
	# pagination for list                                                                                                                   
	my ($offset, $next, $limit);
	$limit = 30;
	$F{'offset'} = 0 if (!$F{'offset'});
	$next = $F{'offset'} + 30;
	$prev = $F{'offset'} - 30 if ($F{'offset'} >= $limit);
	
	my $prev_next = qq |<p class="clear span=15">|;
	$prev_next .= qq | <a href="$thisScript?a=list&amp;offset=$prev&amp;passwd=$F{'passwd'}">Previous</a> |if ($F{'offset'} >= $limit);
	$prev_next .= qq | <a href="$thisScript?a=list&amp;offset=$next&amp;passwd=$F{'passwd'}">Next</a> |;

	
	$sql = qq |
	SELECT id, name, url, shortcut, to_char(ts, 'YYYY MM DD'), ts 
	FROM links
	ORDER BY 6 DESC
	LIMIT ?
	OFFSET ?
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($limit, $F{'offset'});
    $sth->bind_columns (\$id, \$name, \$url, \$shortcut, \$ts, \$t);

	$out .= qq|
	<h2>Links</h2>
	
	<table class="span-14">
	  <tr>
	    <th>Added</th>
	    <th>Name</th>
	    <th>Link</th>
	    <th>Count</th>
	    <th>Info</th>
	    <th>Edit</th>
	  </tr>		
	|;

    while ( $sth->fetch ) {
				
		my ($y, $m, $d) = split (" ", $ts);
		
		# overall count
		my $s = qq |SELECT count(id) FROM tracker WHERE link_id = $id|;
		my $c = $dbh->selectrow_array($s);
	
		
		$out .= qq |
<tr>
 <td>$simple_mon[$m] $d</td>
 <td><h3>$name</h3></td>
 <td><a href="http://stmgrts.org.uk/l/$shortcut" class="highlight">stmgrts.org.uk/l/$shortcut</a></td>
 <td><strong>$c</strong></td>
 <td><a href="?a=stat&amp;id=$id&amp;passwd=$F{'passwd'}">info</a></td>
 <td><a href="?a=edit&amp;id=$id&amp;passwd=$F{'passwd'}">edit</a></td>
</tr>		
		|;
		
    }
    
	$out = qq |
	<div class="span-37">
	$out
	</table>
	
	$prev_next
	
	</div>
	|;

	return($out);
	

}

################################################################################    
sub link_edit {

	my ($sql, $sth, $out);
	my ($id, $name, $url, $shortcut, $ts);
	
	$sql = qq |
	SELECT id, name, url, shortcut, ts 
	FROM links
	WHERE id = ?
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'id'});
    $sth->bind_columns (\$id, \$name, \$url, \$shortcut, \$ts);

	$out .= "\n<h1>Link edit</h1>\n\n";

    while ( $sth->fetch ) {

		
		$out .= qq |
		<fieldset>
		<legend>Edit for $name</legend>
		<p class="push-20"><a href="$thisScript?a=stat_detail&amp;id=$id&amp;name=$name">stats</a></p>
		
	
		<form method="post" action="$thisScript">
				<input type="hidden" name="id" value="$id" />
				<input type="hidden" name="passwd" value="$F{'passwd'}" />
				
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$name" class="text" /></p>
				
				<p><label for="url">url</label><br />
				<input type="text"  name="url" value="$url" class="text" /><br /><em>format: http://www.example.com or https://www.example.com</em></p>
				
				<p><label for="shortcut">Shortcut</label><br />
				<input type="text"  name="shortcut" value="$shortcut" /> <em>only edit if absolutely required</em></p>
								
				<p><button type="submit" name="a" value="link_save"  class="button positive"> <img src="tick.png" alt=""/> Save </button></p>

			</form>
		</fieldset>
		|;

    }
    
		
	$out = qq |
	<div class="span-17">
	$out
	</div>
		
	|;
	return($out);
	
}

################################################################################    
sub link_save {

	# need to test the shortcut to make sure it is unique

	my ($sql, $sth, $out);

	if (!$F{'id'} || $F{'id'} eq "new") {

		# test shortcut is unique
		$sql = qq |SELECT id FROM links WHERE shortcut='$F{'shortcut'}'|;	
		$F{'id'} = $dbh->selectrow_array($sql);
		if ($F{'id'}) {
		
			# there was one... 
			$msg .= qq |THERE ALREADY WAS A LINK WITH THIS SHORTCUT... PLEASE PICK ANOTHER|;
			&print_page(&link_new());
			exit;

		}
		
		$sql = qq |
		INSERT INTO links
		(name, url, shortcut, ts) VALUES (?, ?, ?, ?)|;
		$sth = $dbh->prepare($sql);
		$sth->execute($F{'name'}, $F{'url'}, $F{'shortcut'}, $now);
	
	  	# get new id...
		$F{'name'} =~ s/\'/\'\'/g;
   		$sql = qq |SELECT id FROM links WHERE shortcut = '$F{'shortcut'}'|;
		print STDERR $sql;
		$F{'id'} = $dbh->selectrow_array($sql);
		
		$F{'msg'} = "success";
		$msg .= "Added link $name http://stmgrts.org.uk/l/$F{'shortcut'}";
      
	} else {
	
		# exists
		
		# check if need to update
	   	$sql = qq |UPDATE links SET name=?, url=?, shortcut=? WHERE id=?|;
	   	
	   	$sth = $dbh->prepare($sql);
	    $sth->execute($F{'name'}, $F{'url'}, $F{'shortcut'}, $F{'id'});
	    
	    $F{'msg'} = "success";
	    $msg .= "Updated link $F{'name'} http://stmgrts.org.uk/l/$F{'shortcut'}";

	}
	
	$out .= &formatTweet($F{'name'},$F{'shortcut'});

	return($out);
		
}	

################################################################################    
sub formatTweet {

	my $out = qq |
	
<div class="span-37">
	<fieldset>
       	<legend>Tweet this...</legend>
 			<form method="post" action="$thisScript">
			<input type="hidden" name="passwd" value="$F{'passwd'}" />

<textarea name="tweet" rows="4">
$_[0]
  
  http://stmgrts.org.uk/l/$_[1]
</textarea>

			<p><button type="submit" name="a" value="tweet" class="button positive"> <img src="tick.png" alt=""/> tweet </button></p>

		</form>
	</fieldset>	
	
	|;

	return($out);
}

################################################################################    
sub link_new {

	use String::Random;
	my $shortcut = new String::Random->randpattern("sssss");
	$shortcut =~ s/\//P/g;
	$shortcut =~ s/\./R/g;

    $out .= qq |
<h1>New Link</h1>
<div class="span-37">
	<fieldset>
       	<legend>Create new link</legend>
 			<form method="post" action="$thisScript">
			<input type="hidden" name="id" value="new" />
			<input type="hidden" name="passwd" value="$F{'passwd'}" />

			
				<p><label for="name">Name</label><br />
				<input type="text"  name="name" value="$F{'name'}" class="text" /></p>
				
				<p><label for="url">URL</label><br />
				<input type="text" name="url" value="$F{'url'}" class="text" /></p>

				<p><label for="shortcut">Shortcut</label><br />
				<input type="text" name="shortcut" value="$shortcut" class="text" /></p>

			<p><button type="submit" name="a" value="save" class="button positive"> <img src="tick.png" alt=""/> Save </button></p>

		</form>
	</fieldset>
</div>
	|;

	return($out);
	
}

################################################################################   
sub print_page {

	print <<EndofHTML;
Content-type: text/html

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

	<title>smgrts links</title>
  	
  	<!-- Framework CSS -->
	<link rel="stylesheet" href="screen.css" type="text/css" media="screen, projection">

	<link rel="stylesheet" href="buttons.css" type="text/css" media="screen, projection">

	<link rel="stylesheet" href="print.css" type="text/css" media="print">

  	<!--[if IE]><link rel="stylesheet" href="ie.css" type="text/css" media="screen, projection"><![endif]-->
	
	<link rel="stylesheet" href="http://www.mahnke.net/css/blueprint/blueprint/pages.css" type="text/css" media="screen, projection">
	
	<style type="text/css">
	.big {font-size: 36pt; }
	#sidebar ul { }
	#sidebar li { list-style: none; padding: 1em; margin: 3px 0; background-color: #646498; -moz-border-radius:5px;-webkit-border-radius:5px;border-radius:5px; }
	#sidebar a { color: #fff; text-decoration: none; }
	#sidebar a:hover { text-decoration: underline; font-weight: bold; }
/* = footer */
div#footer {
	background-color: #eee;
	-moz-border-radius:5px;-webkit-border-radius:5px;border-radius:5px;
}

div#footer p {
	font-size: small;
	padding-right: 1em;
	padding-top: 0.5em;
	text-align: right;
	color: #666666;
}

	</style>
	
</head>

<body>

<div class="container show_grid">

	<div id="header" class="span-24 last append-bottom">
			
			<a  href="?a=link&amp;passwd=$F{'passwd'}" title="stmgrts links homepage"><img id="logo" src="http://www.stmgrts.org.uk/images/stmgrts_newsletter_logo.gif" alt="logo" /></a>

	</div><!-- /header -->

<hr class="space" />

	<div id="sidebar" class="span-5">
		<ul id="secondarynav" class="span-5">
			<li><a href="?a=link&amp;passwd=$F{'passwd'}">Home</a></li>
			<li><a href="?a=new&amp;passwd=$F{'passwd'}">New link</a></li>
		</ul>
		
$_[1]
		
	</div><!-- /sidebar -->

	<div id="content" class="prepend-2 span-17 last">

	<div class="span-10 $F{'msg'}">$msg</div>

$_[0]

	</div><!-- /content  -->

	<div id="footer" class="span-24 last">
	
		<p class="prepend-1 span-15 append-1">
			<a href="/aboutus.html">About</a> |
			<a href="/contactus.html">Contact</a> |
			<a href="/conditions.html">Conditions of use</a> |
			<a href="/privacy.html">Privacy Policy</a></p>

		<p id="copyright" class="span-6 append-1 last">Copyright &copy; St Margarets Community Website 2016</p>

	</div><!-- /footer -->

</div><!-- /container -->	
</body>
</html>
EndofHTML

	exit;

}

################################################################################
sub set_tracker {

	# insert a new record into the tracker to force the new url...

    my ($sql, $sth);

    my $now = "now()";
    
    $sql = qq |
INSERT INTO tracker
(link_id, ip, refer, ts)
VALUES
(?,?,?,?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute($F{'id'}, '127.0.0.1', 'admin.cgi', $now);

return();
 
}

################################################################################   
sub stats {

    my ($sql, $sth, $out);
	my ($id, $name, $url, $shortcut, $ts, $count, $refers, $r, $c);
	
	# overall count
	$sql = qq |SELECT count(id) FROM tracker WHERE link_id = $_[0]|;
	$count = $dbh->selectrow_array($sql);
	
	
	# refers
	$sql = qq |SELECT refer, count(id) FROM tracker WHERE link_id= ? GROUP BY  1 ORDER BY 2 desc|;
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'id'});
    $sth->bind_columns (\$r, \$c);
    
	$refers = qq |
	<h3>Refers</h3>
	<table>
	  <tr>
	    <th>URL</th>
	    <th>Count</th>
	  </tr>
	|;
	
	while ( $sth->fetch ) {
		
		if (!$r) {
			$r = "none";
		} else {
			$r = qq |<a href="$r">$r</a>|;
		}
		
		$refers .= qq |
		<tr>
		  <td class="span-5">$r</td>
		  <td>$c</td>
		</tr>
		|;
	}
	$refers .= qq|</table>\n|;
	
	# add chart?
	
	# basic data 
	$sql = qq |
	SELECT id, name, url, shortcut, to_char(ts, 'DD Month YYYY') 
	FROM links
	WHERE id = ?
	|;
	
	$sth = $dbh->prepare($sql);
    $sth->execute($F{'id'});
    $sth->bind_columns (\$id, \$name, \$url, \$shortcut, \$ts);

	$out .= "\n<h1>Link information</h1>\n\n";

    while ( $sth->fetch ) {

		$out .= qq |
		
		<div class="span-37">
	
		<h2>$name</h2>
		
		<h3><a href="http://stmgrts.org.uk/l/$shortcut" class="highlight">stmgrts.org.uk/l/$shortcut</a> &#x21D2; <a href="$url">$url</a></h3>
		
		<p><em>created on: $ts</em></p>
		
		<p class="big">$count Clicks</p>
		
		$refers		
	
			
		</div>
	
		|;
	}
	
	$out .= &formatTweet($name, $shortcut);

	
	return($out);

}

################################################################################   
sub stats_old {

#id integer primary key autoincrement,
#type text, 
#zone_id integer, 
#link_id integer,
#ip text,
#refer text, 
#ts timestamp
#, bkey text);

    my ($sql, $sth, $out);
    my ($id, $count, $clicks,  $name, $date, $fp);
    my (%B, %Z, %IP, %R);
    
    # dates
    if ($F{'date'} eq 'two month ago') {
        $date = qq| AND (ds >= current_date - '3 month'::interval) AND   (ds <= current_date - '2 month'::interval) |;
		&stats_past($date);
    }elsif ($F{'date'} eq 'last month') {
        $date = qq| AND (ds >= current_date - '2 month'::interval) AND   (ds <= current_date - '1 month'::interval) |;
		&stats_past($date);
    } elsif  ($F{'date'} eq 'this month') {
		$date = qq| AND (ds >= current_date - '1 month'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '1 month'::interval) |;
		&stats_today($date);
    } elsif  ($F{'date'} eq 'last week') {
        $date = qq| AND (ds >= current_date - '2 week'::interval) AND   (ds <= current_date - '1 week'::interval) |;
		&stats_past($date);
    } elsif  ($F{'date'} eq 'this week') {
        $date = qq| AND (ds >= current_date - '1 week'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '1 week'::interval) |;
		&stats_today($date);
    } elsif  ($F{'date'} eq 'yesterday') {
        $date = qq| AND (ds >= current_date - '2 day'::interval) AND (ds <= current_date - '1 day'::interval) |;
		&stats_past($date);
        $date = qq| AND (ts >= current_date - '2 day'::interval) AND (ts <= current_date - '1 day'::interval) |;
		&stats_today($date);
    } else {
		$date = qq| AND (ts >= current_date - '1 day'::interval) |;
		&stats_today($date);
    }	

sub stats_today {
	
	my $date = $_[0];
	
    # views of links
    $sql = qq |
select l.id
,      l.name
,      l.file_pointer
,      count(*)
from   tracker t
,      links b
where  l.id = t.link_id
and    t.type = 'image'
$date
group by 1, 2, 3
|;

    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$fp, \$count);
    
    while ( $sth->fetch ) {
	
		$B{$id}           = $name;
		$B{$id}{'count'} += $count;
		$B{$id}{'fp'}     = $fp;
    }
    
    # clicks of links
    $sql = qq |
select l.id
,      l.name
,      count(t.id)
from   tracker t
,      links b
where  l.id = t.link_id
and    t.type = 'link'
$date
group by 1, 2

	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$count);
    
    while ( $sth->fetch ) {
	
		$B{$id}{'link'} += $count;
	
    }
    
    # views of zones
    $sql = qq |
	SELECT z.id, count(distinct t.id), z.name
	FROM tracker t
	LEFT JOIN zones z ON t.zone_id = z.id
	WHERE type = 'image'
	$date
	GROUP BY z.id, z.name
	ORDER BY z.name
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$count, \$name);
    
    while ( $sth->fetch ) {
	
	$Z{$id} = $name;
	$Z{$id}{'count'} += $count;
	
    }
    
    # clicks of zones
    $sql = qq |
	SELECT z.id, count(distinct t.id), z.name
	FROM tracker t
	LEFT JOIN zones z ON t.zone_id = z.id
	WHERE type = 'link'
	$date
	GROUP BY z.id, z.name
	ORDER BY z.name
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$count, \$name);
    
    while ( $sth->fetch ) {
	
		$Z{$id}{'link'} += $count;
	
    }
	
    # views of ip
    $sql = qq |
	SELECT count(distinct t.id)
	FROM tracker t
	WHERE type = 'image'
	$date
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$count);
    
    while ( $sth->fetch ) {
	
		$IP{'count'} += $count;
	
    }
    
    # clicks of ip
    $sql = qq |
	SELECT count(distinct t.id)
	FROM tracker t
	WHERE type = 'link'
	$date
	|;
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$count);
    
    while ( $sth->fetch ) {
	
		$IP{'link'} += $count;
	
    }
    
}

sub stats_past {
	
	my $date = $_[0];
	
    # views of links
	$sql = qq |
	select     l.id
		,      l.name
		,      l.file_pointer
		,      sum(views)
		,      sum(clicks) 
	from tracker_summary ts
	,    links b
	where 
		ts.link_id = l.id
		$date
	group by 1,2,3
	order by 1
	|;

	#print STDERR "$sql\n";
	#$msg .= "$sql\n";

    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$fp, \$count, \$clicks);
    
    while ( $sth->fetch ) {
	
		$B{$id} = $name;
		$B{$id}{'count'} = $count;
		$B{$id}{'fp'}    = $fp;
		$B{$id}{'link'}  = $clicks;
    }
    
    # views of zones
	$sql = qq |
	select     z.id
		,      z.name
		,      sum(views)
		,      sum(clicks) 
	from tracker_summary ts
	,    zones z 
	where 
		ts.zone_id = z.id
		$date
	group by 1, 2 
	order by 1
	|;
	
	#print STDERR "$sql\n";
	#$msg .= "$sql\n";
    
    $sth = $dbh->prepare($sql);
    $sth->execute();
    $sth->bind_columns (\$id, \$name, \$count, \$clicks);
    
    while ( $sth->fetch ) {
	
		$Z{$id} = $name;
		$Z{$id}{'count'} = $count;
		$Z{$id}{'link'} = $clicks;
	
    }
}

	# build up page
    
    $out .= qq |

	<form method="post" action="$thisScript?">
	<p><label for="date">Date range</label>
	<select name="date">
	<option value="$F{'date'}">$F{'date'}</option>
	<option value=""></option>
	<option value="today">today</option>
	<option value="yesterday">yesterday</option>
	<option value="this week">this week</option>
	<option value="last week">last week</option>
	<option value="this month">this month</option>
	<option value="last month">last month</option>
	<option value="two months ago">two months ago</option>
	</select></p>
	<p><button type="submit" name="a" value="stats"  class="button positive"> <img src="tick.png" alt=""/> Get stats! </button></p>
	</form>
<hr>

	<table>
	<tr>
	<th colspan="2">links</th>
	<th>Views</th>
	<th>Clicks</th>
	<th>Percent</th>
	</tr>
	|;
    
    foreach (sort keys %B) {
	
		my $pct = int($B{$_}{'link'} / $B{$_}{'count'} * 10000) if ( $B{$_}{'count'} );
		$pct = $pct/100 if ($pct);
		
		next if ($B{$_} =~ /HASH/);
		
		$out .= qq |
	    
	    <tr>
	    <td><a href="$thisScript?a=stat_detail&amp;img=$B{$_}{'fp'}&amp;id=$_&amp;name=$B{$_}"><img src="$B{$_}{'fp'}" height="50" /></a></td>
	    <td>$B{$_}</td>
	    <td>$B{$_}{'count'}</td>
	    <td>$B{$_}{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	
    }
    
    $out .= qq |
	<tr>
	<th>Zones</th>
	</tr>
	|;
    
    foreach (sort keys %Z) {
	
	my $pct = int($Z{$_}{'link'} / $Z{$_}{'count'} * 10000) if ($Z{$_}{'count'});
	$pct = $pct/100 if ($pct);
	
	
	$out .= qq |
	    
	    <tr>
	    <td>$Z{$_}</td>
	    <td>$Z{$_}{'count'}</td>
	    <td>$Z{$_}{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	
    }
    
    $out .= qq |
	<tr>
	<th>IP</th>
	</tr>
	|;
    
    foreach (sort keys %IP) {
	
	my $pct = int($IP{$_}{'link'} / $IP{$_}{'count'} * 10000) if ($IP{$_}{'count'});
	$pct = $pct/100 if ($pct);
	
	$out .= qq |
	    
	    <tr>
	    <td>users</td>
	    <td>$IP{'count'}</td>
	    <td>$IP{'link'}</td>
	    <td>$pct %</td>
	    </tr>
	    |;
	last;
	
    }

    $out .= qq |
	    </table>
	    |;

    
    return($out);
    
}

################################################################################
sub stat_detail {
	
	
	my $sql = qq ~
	select 
		to_char(ts, 'YYYY WW'), 
		sum(case when type='image' then 1 else 0 end), 
		sum(case when type='link' then 1 else 0 end)
	from   tracker
	where  link_id = $F{'id'}
	group by 1
	order by 1
	~;
	
	$sql = qq ~
	select 
		to_char(ds, 'YYYY WW'), 
		sum(views), 
		sum(clicks) 
	from tracker_summary 
	where 
		link_id = $F{'id'}
	group by 1 
	order by 1
	~;
	
	my ($chart,$table) = &gchart($sql, "$F{'name'}", "views|clicks");

	# monthly chart
	$sql = qq ~
	select 
		to_char(ds, 'YYYY MM'), 
		sum(views), 
		sum(clicks) 
	from tracker_summary 
	where 
		link_id = $F{'id'}
	group by 1 
	order by 1
	~;
	
	my ($chart_m,$table_m) = &gchart($sql, "$F{'name'}", "views|clicks");

	
	my $out = qq ~
	
	<h2>$F{'name'}</h2>

	<div><img src="$F{'img'}" class="left" /></div>

       	$chart

	<table>
	<tr><th>Week Year</th><th>Views</th><th>Clicks</th></tr>
	$table
	</table>

       	$chart_m

	<table>
	<tr><th>Month Year</th><th>Views</th><th>Clicks</th></tr>
	$table_m
	</table>
	
	<pre>
	$sql
	</pre>
	
	~;
	
	return($out);
	
}

################################################################################
sub gchart {
	

	my ($cat, $count, $sum, $t_count, $t_sum, $title, $stitle, $mag_count, $mag_sum, $mag, $all_count, $week, $w, $month, $m, $gc_data_1, $gc_data_2, $gc_axis_x, $gc_min_1, $gc_max_1, $gc_min_2, $gc_max_2, $gc_axis_x, $gc_axis_years, $FLAG_adj, $prev_y, $y_a, $gc_x1, $gc_x2, $output, $table) = "";

	$sth = $dbh->prepare($_[0]);
	$sth->execute ();
	$sth->bind_columns (\$week, \$count, \$sum);

	while ( $sth->fetch ) {

	   	#($month, $m, $y) = &nice_month($month);
		($y, $w) = split (" ", $week);
	   	$t_count += $count;
	   	$t_sum   += $sum;

#		if ($m == $current_month && $y == $current_year) {
#			$count = int($count*$date_pct);
#			$sum = int($sum*$date_pct);
#			$FLAG_adj = "*";
#		}
		$gc_axis_x .= "|".$w;
		$gc_data_1 .= "$count,";
		$gc_min_1 = $count if ($count < $gc_min_1 || !$gc_min_1);
		$gc_max_1 = $count if ($count > $gc_max_1);
		$gc_data_2 .= "$sum,";
		$gc_min_2 = $sum if ($sum < $gc_min_2 || !$gc_min_2);
		$gc_max_2 = $sum if ($sum > $gc_max_2);

        # year axis
        $y_a = "";
		$y_a = $y if ($y != $prev_y);
		$gc_axis_years .= "|$y_a";
		$prev_y = $y;

		$table .= qq |<tr><td>$w $y</td><td align\=\"right\">$count</td><td align\=\"right\">$sum</td></tr>\n|;

	}

	#$t_sum = &decimals($t_sum);

	$FLAG_adj = qq~<em>* this month's figures estimated</em>~ if ($FLAG_adj);
	$table .= qq|<tr class\=\"total\"><td>total<\/td><td align\=\"right\">$t_count<\/td><td align\=\"right\">$t_sum<\/td><\/tr><tr><td colspan\=\"3\" align\=\"right\">$FLAG_adj</tr></table>\n|;

 	$gc_x1 = &g_labels($gc_max_1);
   	$gc_x2 = &g_labels($gc_max_2);
	$gc_max_1 = &max_10($gc_max_1);
	$gc_max_2 = &max_10($gc_max_2);
    $gc_min_1 = 0;
    $gc_min_2 = 0;

	#$gc_axis_years = &gc_years;

	chop($gc_data_1);
	chop($gc_data_2);

	my $chart = qq ~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_2,$gc_max_2&chd=t:$gc_data_1|$gc_data_2&chs=700x300&chco=009900,0000ff&chxt=x,y,r,x&chxl=0:$gc_axis_x|1:|$gc_x1|2:|$gc_x2|3:$gc_axis_years&chls=2,1,0|2,1,0&chdl=$_[2]&chtt=$_[1]+Overall+by+Week
	~;

	my $sparkline = qq~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_2,$gc_max_2&chd=t:$gc_data_1|$gc_data_2&chs=300x100&chco=009900,0000ff&chtt=$_[1]+Overall+by+Week
	~;

	$output = qq ~
	<p><img src="$chart" /></p>
	~;
	
	return($output, $table);
	
}

################################################################################
sub gchart_twoline {
	
	# pass $sql, 0 - title, 1 - axis lables

	my ($cat, $count, $sum, $t_count, $t_sum, $title, $stitle, $mag_count, $mag_sum, $mag, $all_count, $month, $m, $gc_data_1, $gc_data_2, $gc_axis_x, $gc_min_1, $gc_max_1, $gc_min_2, $gc_max_2, $gc_axis_x, $gc_axis_years, $FLAG_adj, $prev_y, $y_a, $gc_x1, $gc_x2, $output, $table) = "";

	$sth = $dbh->prepare($_[0]);
	$sth->execute ();
	$sth->bind_columns (\$month, \$count, \$sum);

	while ( $sth->fetch ) {

	   	($month, $m, $y) = &nice_month($month);
	   	$t_count += $count;
	   	$t_sum   += $sum;

		$gc_axis_x .= "|".&simple_date($month);
		$gc_data_1 .= "$count,";
		$gc_min_1 = $count if ($count < $gc_min_1 || !$gc_min_1);
		$gc_max_1 = $count if ($count > $gc_max_1);
		$gc_data_2 .= "$sum,";
		$gc_min_2 = $sum if ($sum < $gc_min_2 || !$gc_min_2);
		$gc_max_2 = $sum if ($sum > $gc_max_2);

       	# year axis
		$y_a = "";
		$y_a = $y if ($y != $prev_y);
		$gc_axis_years .= "|$y_a";
		$prev_y = $y;

		# build table
		$table .= qq ~<tr><td>$month $year</td><td>$count</td><td>$sum</td></tr>\n~;

	}

	$t_sum = &decimals($t_sum);

   $gc_x1 = &g_labels($gc_max_1);
   $gc_x2 = &g_labels($gc_max_2);
	$gc_max_1 = &max_10($gc_max_1);
	$gc_max_2 = &max_10($gc_max_2);

   $gc_min_1 = 0;
   $gc_min_2 = 0;

	chop($gc_data_1);
	chop($gc_data_2);

	my $chart = qq ~
	http://chart.apis.google.com/chart?cht=lc&chds=$gc_min_1,$gc_max_1,$gc_min_1,$gc_max_1&chd=t:$gc_data_1|$gc_data_2&chs=800x300&chco=009900,0000ff&chxt=x,y,r,x&chxl=0:$gc_axis_x|1:|$gc_x1|2:|$gc_x1|3:$gc_axis_years&chls=2,1,0|2,1,0&chdl=$_[2]&chtt=$_[1]+Overall+by+Month
	~;

	$output = qq ~
	<p><img src="$chart" /></p>
	~;
	
	return($output, $table);
	
}

################################################################################
sub g_labels {

   # in put max
   my $max = $_[0] * 1.1;
   my $n_labels = 5;
   my $n = 0;
   my $output = "";
   for ($n=0; $n < $n_labels; $n++) {
       my $dp = ($max/$n_labels) * $n;
       $output .= int($dp)."|";
   }
	$output .= int($max);
   return ($output);
}

################################################################################
sub pct {

	return() if (!$_[1]);

	my $pct = ($_[0]/$_[1]) * 100;
	$pct    = &decimals($pct);

	return($pct);
	
}

################################################################################
sub dec {

	return() if (!$_[1]);

	my $d = ($_[0]/$_[1]);
	$d    = &decimals($d);
	
	return($d);
	
}

################################################################################
sub decimals {

	# adds decimals to currency
	my $out;
	
	my ($n, $d) = split (/\./, $_[0]);

	$d = substr($d, 0, 2) if (length($d) > 2);

	if (length($d) == 0) {
		# no decimal... add 00
       $out = $n.".00";
   } elsif(length($d) == 1) {
       # only one, so add 0
       $out = $n.".".$d."0";
   } else {
       # its ok
       $out = $n.".".$d;
   }

   return($out);

}

################################################################################
sub nice_month {
		
	# takes YYYY MM Month > returns YYYY Month
	my ($y,$mm, $mon) = split (" ", $_[0]);
	my $out = "$mon $y";
	return($out, $mm, $y);
	
}

################################################################################
sub simple_date {	
	
	# takes Month YYYY > returns Mon
	my ($mon, $y) = split (" ", $_[0]);
	my $out = substr ($mon, 0, 3);
	return($out);
	
}

################################################################################
sub min_10 {
	
	my $o = $_[0] * 0.9;
	$o = int ($o);
	return ($o);
	
}

################################################################################
sub max_10 {
	
	my $o = $_[0] * 1.1;
	$o = int ($o);
	return ($o);
	
}
