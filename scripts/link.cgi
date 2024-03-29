#!/usr/bin/perl

##############################################################
##############################################################
#
# link.cgi
#
#  gets an link and returns it
#
#  input: 
#         shortcut
#
##############################################################
##############################################################


use CGI::Lite;
use DBI;

my $dbh = DBI->connect("dbi:Pg:dbname=stmgrtslinks","pmahnke","Shi11t0P",{ RaiseError => 1, AutoCommit => 1    });
my $date      = `date +'%Y-%m-%d'`;
chop($date);


################################################################
if ($ENV{'CONTENT_LENGTH'} || $ENV{'QUERY_STRING'}) {

    $cgi = new CGI::Lite;
    %F = $cgi->parse_form_data;
    
} else {
    
    # nothing submitted... so PANIC!!!
    exit;
   
}

if ($F{'shortcut'}) {

    &get_link();
    exit;

}

exit;



###############################################
sub get_link {

    # requires zone_id
    my ($sql, $sth, $id, $url);

    $sql = qq |
SELECT id, url
FROM links
WHERE shortcut = ?
LIMIT 1
	|;


    $sth = $dbh->prepare($sql);

    $sth->execute($F{'shortcut'});

    $sth->bind_columns (\$id, \$url);

    my $google = qq |utm_source=stmgrtslinks&utm_medium=url_shortner&utm_term=$F{'shortcut'}&utm_campaign=shortner|;

    while ( $sth->fetch ) {

	$url = qq |http://$url| if ($url !~ /http/);
	
	if ($url) {
	    
	    if ($url =~ /(stmgrts|mystmargarets)/) {
		# if internal link, add google code
		if ($url =~ /\?/) {
		    $url .= "&".$google;
		} else {
		    $url .= "?".$google;
		}
		$url =~ s/stmgrts.org.uk/stmargarets.london/;
	    }
	    # print STDERR "looking at $url";
	    
	    &tracker($id, $ENV{'REMOTE_ADDR'}, $ENV{'HTTP_REFERER'});

	    print "Status: 301 Moved Permanently\nLocation: $url\n\n";

	    
	    
	} else {
	    
	    print "Status: 302 Found\nLocation: $ENV{'HTTP_REFERER'}\n\n";
	}
    }
    return();
}

########################################################
sub tracker {

    my ($sql, $sth);

    my $now = "now()";
    
    $sql = qq |
INSERT INTO tracker
(link_id, ip, refer, ts)
VALUES
(?,?,?,?)
    |;

$sth = $dbh->prepare($sql);
$sth->execute($_[0], $_[1], $_[2], $now);

return();
 
}
