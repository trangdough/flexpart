#! /bin/csh -f
#
# c-shell script to download selected files from gdex.ucar.edu using Wget
# NOTE: if you want to run under a different shell, make sure you change
#       the 'set' commands according to your shell's syntax
# after you save the file, don't forget to make it executable
#   i.e. - "chmod 755 <name_of_script>"
#
# Experienced Wget Users: add additional command-line flags here
#   Use the -r (--recursive) option with care
set opts = "-N"
#
set cert_opt = ""
# If you get a certificate verification error (version 1.10 or higher),
# uncomment the following line:
#set cert_opt = "--no-check-certificate"
#
# download the file(s)
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020300.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020306.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020312.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020318.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020400.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020406.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020412.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020418.f03.grib2
wget $cert_opt $opts https://osdf-director.osg-htc.org/ncar/gdex/d083003/2023/202302/gdas1.fnl0p25.2023020500.f03.grib2
