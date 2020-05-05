\copy (SELECT 'drop database "'||datname||'";' FROM pg_database d JOIN pg_user u ON (d.datdba = u.usesysid) WHERE d.datistemplate=false AND d.datname like 'template_%' AND u.usename = 'bar') TO '/home/bar/_remove_template.sql';
\i /home/bar/_remove_template.sql

