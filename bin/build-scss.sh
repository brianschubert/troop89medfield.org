#!/usr/bin/env bash
# Compiles project ``.scss`` files to a single, servable ``.css``.

# For ease of use during development, one should consider using
# an IDE based file watcher rather than running this script. In the
# future, this script may be replaced by a Makefile or by a python
# package that provides support for compiling ``scss`` files inside of
# Django.
#
# This script depends on the existence of either the ``libsass-python``
# or ``sassc`` wrapper for the ``libsass``library. Both of these provide
# a ``sassc`` executable.

# The arguments to pass to the ``libsass`` compiler.
SASSC_ARGS="-s compressed"

STATIC_DIR="./assets"

# Create the target directory for css files if it does not already exist.
mkdir -p ${STATIC_DIR}/css

sassc ${SASSC_ARGS} ${STATIC_DIR}/scss/output.scss ${STATIC_DIR}/css/output.css
