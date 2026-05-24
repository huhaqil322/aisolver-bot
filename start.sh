     #!/bin/bash                                                                                                                                                           
     #!/bin/bash                                                                                                                                                                            91,768 tokens                           
#!/bin/ba

#!/bin/bas
set -e
alembic upgrade head
exec uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
