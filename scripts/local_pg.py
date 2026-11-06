"""Local-only, read-only PostgreSQL access; credentials never enter artifacts."""
from dotenv import dotenv_values
import psycopg2


def connect(env_file, timeout=1800000):
    env = dotenv_values(env_file)
    prefix = 'LOCAL_DB_' if env.get('LOCAL_DB_HOST') else 'DB_'
    assert env.get(prefix+'HOST', '').lower().rstrip('.') in ('localhost', '127.0.0.1', '::1')
    cfg = {k: env.get(prefix+v) for k, v in [('host','HOST'),('port','PORT'),('dbname','NAME'),('user','USER'),('password','PASSWORD')]}
    try:
        conn = psycopg2.connect(**cfg, connect_timeout=15, application_name='pharma_training_readonly',
                               options=f'-c default_transaction_read_only=on -c statement_timeout={int(timeout)} -c lock_timeout=3000 -c timezone=UTC')
    except psycopg2.OperationalError:
        raise RuntimeError('Local PostgreSQL connection failed; credentials suppressed') from None
    conn.set_session(readonly=True, isolation_level='REPEATABLE READ')
    with conn.cursor() as q:
        q.execute("select current_setting('transaction_read_only')")
        assert q.fetchone()[0] == 'on'
    return conn
