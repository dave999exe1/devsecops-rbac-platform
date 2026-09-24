from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(
    title="DevSecOps RBAC API Gateway",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "identity": "http://identity-service:8000",
    "rbac": "http://rbac-service:8000",
    "sync": "http://sync-service:8000",
    "audit": "http://audit-service:8000",
}


@app.get("/health")
def health():
    return {
        "service": "api-gateway",
        "status": "healthy",
    }


@app.get("/api/{service}/health")
async def service_health(service: str):
    if service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown service: {service}",
        )

    url = f"{SERVICES[service]}/health"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)

        return {
            "gateway": "healthy",
            "service": service,
            "service_status": response.json(),
        }

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Service unavailable: {service}",
        ) from exc


@app.api_route(
    "/api/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)
async def proxy_request(
    service: str,
    path: str,
    request: Request,
):
    if service not in SERVICES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown service: {service}",
        )

    url = f"{SERVICES[service]}/{path}"

    body = await request.body()

    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params,
            )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={
                "content-type": response.headers.get(
                    "content-type",
                    "application/json",
                )
            },
        )

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Service unavailable: {service}",
        ) from exc
