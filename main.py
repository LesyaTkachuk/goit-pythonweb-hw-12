from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from src.api import contacts, groups, utils, auth, users
from slowapi.errors import RateLimitExceeded
from src.conf import messages

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limi_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": messages.EXCEED_REQUESTS_LIMIT},
    )


app.include_router(contacts.router, prefix="/api")
app.include_router(groups.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
