#!/usr/bin/env bash
gunicorn --timeout 120 app:app