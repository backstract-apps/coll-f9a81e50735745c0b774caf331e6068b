from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import models
import uvicorn
from routes import router
import time
import logging_loki
from multiprocessing import Queue
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # Re-add this import
import logging
import sys
import os
from telemetry_config import setup_telemetry_and_logging

setup_telemetry_and_logging()


# Database setup
models.Base.metadata.create_all(bind=engine)

# Prometheus core metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency',
                            ['method', 'endpoint', 'http_status'])
IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP requests in progress')

app = FastAPI(title='Backstract Generated APIs - coll-f9a81e50735745c0b774caf331e6068b', debug=False,
              docs_url='/elated-stonebraker-06ebce58581011f0913fd6edd7103f1a85/docs',
              openapi_url='/elated-stonebraker-06ebce58581011f0913fd6edd7103f1a85/openapi.json')


FastAPIInstrumentor.instrument_app(app)  # Re-add this line

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix='/elated-stonebraker-06ebce58581011f0913fd6edd7103f1a85/api',
    tags=['APIs v1']
)


# Middleware for Prometheus metrics
@app.middleware('http')
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    path = request.url.path
    start_time = time.time()
    status_code=None

    IN_PROGRESS.inc()  # Increment in-progress requests

    try:
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time()-start_time)*1000
        if "/metrics" not in request.url.path and "/loki" not in request.url.path:
            status_code = response.status_code
            emoji = "➡️"
            if 200 <= status_code < 300:
                emoji += " ✅"  # Success
                log_level = logger.info
            elif 300 <= status_code < 400:
                emoji += " ↪️"  # Redirection
                log_level = logger.info
            elif 400 <= status_code < 500:
                emoji += " ⚠️"  # Client Error
                log_level = logger.warning
            else:  # 500 and above
                emoji += " ❌"  # Server Error
                log_level = logger.error

            log_level(
                f"{emoji} {request.method} {request.url.path} Status: {status_code} response:{response} ⏱️ Time: {process_time:.2f}ms"
            )
    except Exception as e:
        status_code = 500  # Internal server error
        raise e
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=path, http_status=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path, http_status=status_code).observe(duration)
        IN_PROGRESS.dec()  # Decrement in-progress requests

    return response


# Prometheus' metrics endpoint
prometheus_app = make_asgi_app()
app.mount('/metrics', prometheus_app)

def main():
    uvicorn.run('main:app', host='127.0.0.1', port=7070, reload=True)


if __name__ == '__main__':
    main()