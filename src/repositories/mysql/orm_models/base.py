import os
import socket
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app")
DB_NAME = os.getenv("DB_NAME", "movie_rental")

def _can_resolve(host: str) -> bool:
	try:
		socket.gethostbyname(host)
		return True
	except socket.gaierror:
		return False

def _build_url(host: str, port: int) -> str:
	return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{host}:{port}/{DB_NAME}"

# Fallback: if running locally (outside docker) 'mysql' may not resolve; try localhost:3307 (compose mapped port)
primary_host = DB_HOST
primary_port = DB_PORT
fallback_host = os.getenv("DB_FALLBACK_HOST", "localhost")
fallback_port = int(os.getenv("DB_FALLBACK_PORT", "3307"))

candidate_urls = []
if _can_resolve(primary_host):
	candidate_urls.append(_build_url(primary_host, primary_port))
else:
	# push fallback first if primary cannot resolve
	candidate_urls.append(_build_url(fallback_host, fallback_port))
	# also keep primary (DNS might appear later e.g. after docker starts)
	candidate_urls.append(_build_url(primary_host, primary_port))

Base = declarative_base()
engine = None

last_error: Exception | None = None
for idx, url in enumerate(candidate_urls):
	for attempt in range(1, 6):  # up to 5 attempts each URL
		try:
			engine = create_engine(url, pool_pre_ping=True)
			# quick test connection
			with engine.connect() as conn:
				conn.execute(text("SELECT 1"))  # type: ignore[name-defined]
			print(f"[MySQL] Connected using URL #{idx+1}: {url}")
			break
		except OperationalError as e:
			last_error = e
			print(f"[MySQL] OperationalError attempt {attempt}/5 for {url}: {e}")
			time.sleep(2)
		except Exception as e:
			last_error = e
			print(f"[MySQL] General error attempt {attempt}/5 for {url}: {e}")
			time.sleep(2)
	if engine is not None:
		break

if engine is None:
	raise RuntimeError(f"Could not connect to any MySQL URL. Last error: {last_error}")

SessionLocal = sessionmaker(bind=engine)

__all__ = ["Base", "engine", "SessionLocal"]
