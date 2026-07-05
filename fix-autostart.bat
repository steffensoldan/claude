@echo off
:: Startet fix-autostart.ps1 mit Admin-Rechten (UAC-Prompt erscheint einmalig)
powershell -ExecutionPolicy Bypass -Command "Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File ""%~dp0fix-autostart.ps1""'"
