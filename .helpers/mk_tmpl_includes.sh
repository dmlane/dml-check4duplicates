#!/usr/bin/env bash
: << DOCXX
#------------------------------------------------------------------------------
#          Name:    mk_tmpl_includes.sh
#   Description:    Regenerates the includes part of the brew tmpl file
#    Parameters:    None
#
#------------------------------------------------------------------------------
DOCXX

. ${0%/*}/.bash.common

# Fail if any of these commands are missing (bumpver not needed by this script
#                                            but needed by the project)
require_commands gsed
[ $PROJECT_NAME ] || fail "Expected to find PROJECT_NAME from MAKE environment"
[ $WORK_DIR ] || fail "Expected to find WORK_DIR from MAKE environment"
[ $HELPER ] || fail "Expected to find HELPER from MAKE environment"

WF=$(mktemp -d)
highlight "Getting a list of packages from Poetry"
poetry show --only main >${WF}/poetry.packages

highlight "Fetching python resources for ^$PROJECT_NAME^"
${HELPER}/get_pypi_info.py ${WF}/poetry.packages >${WF}.include
if [ $? -ne 0 ] ; then
	rm -rf $WF
	fail "'${HELPER}/get_pypi_info.py ${WF}/poetry.package' returned error"
fi

gsed "/#---START-RESOURCES---/,/#---END-RESOURCES---/!b;//!d;/#---START-RESOURCES---/r ${WF}.include" ${PROJECT_NAME}.tmpl >${PROJECT_NAME}.tmpl.new
if [ $? -ne 0 ] ; then
	rm -rf ${WF}
	fail "gsed had a problem"
fi
mv -f ${PROJECT_NAME}.tmpl.new ${PROJECT_NAME}.tmpl

rm -rf ${WF}
