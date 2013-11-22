@ECHO OFF
REM $Id$
REM 
REM $URL$
REM 
REM Copyright (c) 2010 foption
REM 
REM Permission is hereby granted, free of charge, to any person obtaining a copy
REM of this software and associated documentation files (the "Software"), to deal
REM in the Software without restriction, including without limitation the rights
REM to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
REM copies of the Software, and to permit persons to whom the Software is
REM furnished to do so, subject to the following conditions:
REM 
REM The above copyright notice and this permission notice shall be included in
REM all copies or substantial portions of the Software.
REM 
REM THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
REM IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
REM FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
REM AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
REM LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
REM OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
REM THE SOFTWARE.
REM 
REM Since: Jan 24, 2012
REM Author: Mario Steinhoff
REM

SETLOCAL

SET BASE=%~dp0..
SET PYTHONPATH=%PYTHONPATH%;%BASE%\src\python

SET FPTBOT_CONFIG=%BASE%\config

SET PYTHON_BINARY=python
SET PYTHON_SCRIPT=%BASE%\src\python\tools\config.py
SET PYTHON_ARGS=%*

%PYTHON_BINARY% "%PYTHON_SCRIPT%" %PYTHON_ARGS%
