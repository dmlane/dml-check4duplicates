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
require_commands brew gsed
[ $PROJECT_NAME ] || fail "Expected to find PROJECT_NAME from MAKE environment"

WF=$(mktemp)
highlight "Fetching python resources for ^$PROJECT_NAME^"
brew update-python-resources -p $PROJECT_NAME >$WF
if [ $? -ne 0 ] ; then
	rm $WF
	fail "'brew update-python-resources $PROJECT_NAME' returned error"
fi

gsed "/#---START-RESOURCES---/,/#---END-RESOURCES---/!b;//!d;/#---START-RESOURCES---/r ${WF}" ${PROJECT_NAME}.tmpl >${PROJECT_NAME}.tmpl.new
mv -f ${PROJECT_NAME}.tmpl.new ${PROJECT_NAME}.tmpl

rm ${WF}
