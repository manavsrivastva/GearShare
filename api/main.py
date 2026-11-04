
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field

from gearshare import GearShare
from errors import (
    CustomerNotFoundError,
    InvalidSKUError,
    DisplayItemRentalError,
    UnpaidFineError,
    TierLimitError,
    DuplicateRentalError,
    ItemUnavailableError,
)


gearshare = None


# --------------------------------------------------
# APPLICATION LIFECYCLE
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global gearshare

    database_path = os.getenv(
        "GEARSHARE_DB_PATH",
        "gearshare.db"
    )

    gearshare = GearShare(db_path=database_path)

    yield

    gearshare.close()


app = FastAPI(
    title="GearShare API",
    description="HTTP API for GearShare",
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

frontend_origin = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class RentalRequest(BaseModel):
    customer_id: str
    sku: str


class AddGearRequest(BaseModel):
    sku: str = Field(pattern=r"^\d{10}$")
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    item_type: str
    price: float = Field(gt=0)
    total_units: int = Field(ge=1)
    weight_g: int = Field(default=0, ge=0)
    tags: list[str] = Field(default_factory=list)


# --------------------------------------------------
# ERROR HANDLING HELPERS
# --------------------------------------------------

def error_response(error_code, message, status_code):
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": error_code,
            "message": message,
        },
    )


def translate_rental_error(exc, customer_id, sku):

    message = str(exc)

    if isinstance(exc, CustomerNotFoundError):
        error_response(
            "CustomerNotFoundError",
            f"No customer with ID {customer_id}.",
            404,
        )

    if isinstance(exc, InvalidSKUError):

        if not str(sku).isdigit() or len(str(sku)) != 10:
            error_response(
                "InvalidSKUError",
                "SKU must be exactly 10 digits.",
                422,
            )

        error_response(
            "ItemNotFoundError",
            f"No item with SKU {sku}.",
            404,
        )

    if isinstance(exc, DisplayItemRentalError):
        item = gearshare.items[str(sku)]

        error_response(
            "R1",
            f"'{item.name}' is a display item and cannot be rented.",
            409,
        )

    if isinstance(exc, UnpaidFineError):
        customer = gearshare.customers[customer_id]
        unpaid = gearshare.get_unpaid_fines(customer_id)

        error_response(
            "R4",
            f"{customer.name} has unpaid fines of ₹{unpaid:.0f} (limit ₹500).",
            409,
        )

    if isinstance(exc, TierLimitError):
        error_response(
            "TierLimitError",
            "You have reached your membership rental limit.",
            409,
        )

    if isinstance(exc, DuplicateRentalError):
        customer = gearshare.customers[customer_id]
        item = gearshare.items[str(sku)]

        error_response(
            "R8",
            f"{customer.name} already has a unit of '{item.name}'.",
            409,
        )

    if isinstance(exc, ItemUnavailableError):
        error_response(
            "ItemUnavailableError",
            message,
            409,
        )

    error_response(
        "GearShareError",
        message,
        400,
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------------------------------------
# GET ALL GEAR
# --------------------------------------------------

@app.get("/gear")
def get_gear(
    q: str = Query(default=""),
    category: str = Query(default=""),
    sort: str = Query(default="name"),
):

    items = gearshare.catalogue()

    search_text = q.strip().lower()

    if search_text:
        items = [
            item for item in items
            if (
                search_text in item.name.lower()
                or search_text in item.sku.lower()
                or any(
                    search_text in tag
                    for tag in item.tags
                )
            )
        ]

    if category and category.lower() != "all":
        items = [
            item for item in items
            if item.category.lower() == category.lower()
        ]

    sort_options = {
        "name": lambda item: item.name.lower(),
        "category": lambda item: item.category.lower(),
        "price": lambda item: item.price,
    }

    if sort not in sort_options:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "ValidationError",
                "message": "Sort must be name, category or price.",
            },
        )

    items.sort(key=sort_options[sort])

    return [
        {
            "sku": item.sku,
            "name": item.name,
            "tags": item.tags,
            "category": item.category,
            "item_type": type(item).__name__,
            "price": item.price,
            "available_units": gearshare.get_available_units(item.sku),
            "total_units": item.total_units,
            "weight_g": item.weight_g,
            "can_be_rented": item.can_be_rented(),
        }
        for item in items
    ]


# --------------------------------------------------
# GET ONE GEAR ITEM
# --------------------------------------------------

@app.get("/gear/{sku}")
def get_gear_item(sku: str):

    item = gearshare.items.get(sku)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ItemNotFoundError",
                "message": f"No item with SKU {sku}.",
            },
        )

    return {
        "sku": item.sku,
        "name": item.name,
        "tags": item.tags,
        "category": item.category,
        "item_type": type(item).__name__,
        "price": item.price,
        "available_units": gearshare.get_available_units(sku),
        "total_units": item.total_units,
        "weight_g": item.weight_g,
        "can_be_rented": item.can_be_rented(),
    }
# --------------------------------------------------
# ADD NEW GEAR ITEM
# --------------------------------------------------

@app.post("/gear", status_code=201)
def add_gear(request: AddGearRequest):

    try:
        item = gearshare.add_item(
            sku=request.sku,
            name=request.name,
            category=request.category,
            item_type=request.item_type,
            price=request.price,
            total_units=request.total_units,
            weight_g=request.weight_g,
            tags=request.tags,
        )

        return {
            "message": "Equipment added successfully.",
            "item": {
                "sku": item.sku,
                "name": item.name,
                "tags": item.tags,
                "category": item.category,
                "item_type": type(item).__name__,
                "price": item.price,
                "available_units": gearshare.get_available_units(item.sku),
                "total_units": item.total_units,
                "weight_g": item.weight_g,
                "can_be_rented": item.can_be_rented(),
            },
        }

    except ValueError as exc:

        message = str(exc)

        if "already exists" in message.lower():
            error_response("DuplicateSKUError", message, 409)

        error_response("ValidationError", message, 422)


# --------------------------------------------------
# CREATE RENTAL
# --------------------------------------------------

@app.post("/rentals", status_code=201)
def create_rental(request: RentalRequest):

    try:
        rental = gearshare.rent_item(
            request.customer_id,
            request.sku,
        )

        return {
            "rental_id": rental.rental_id,
            "due_date": rental.due_date.isoformat(),
        }

    except (
        CustomerNotFoundError,
        InvalidSKUError,
        DisplayItemRentalError,
        UnpaidFineError,
        TierLimitError,
        DuplicateRentalError,
        ItemUnavailableError,
    ) as exc:

        translate_rental_error(
            exc,
            request.customer_id,
            request.sku,
        )


# --------------------------------------------------
# RETURN RENTAL
# --------------------------------------------------

@app.post("/rentals/{rental_id}/return")
def return_rental(rental_id: str):

    rental = next(
        (
            item for item in gearshare.rentals
            if item.rental_id == rental_id
        ),
        None,
    )

    if rental is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "RentalNotFoundError",
                "message": f"No rental with ID {rental_id}.",
            },
        )

    if not rental.is_active:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "RentalAlreadyReturnedError",
                "message": "Rental has already been returned.",
            },
        )

    days_late = rental.days_late(gearshare.today)

    result = gearshare.return_item(rental_id)

    queue = gearshare.waiting_lists[rental.sku]
    next_customer = None

    if queue:
        next_customer = gearshare.customers[queue[0]].name

    return {
        "rental_id": result["rental_id"],
        "days_late": days_late,
        "fine": result["late_fee"],
        "next_in_waiting_list": next_customer,
    }


# --------------------------------------------------
# GET CUSTOMER RENTALS
# --------------------------------------------------

@app.get("/customers/{customer_id}/rentals")
def get_customer_rentals(customer_id: str):

    if customer_id not in gearshare.customers:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CustomerNotFoundError",
                "message": f"No customer with ID {customer_id}.",
            },
        )

    customer = gearshare.customers[customer_id]

    active_rentals = gearshare.get_active_rentals(customer_id)

    return {
        "customer": customer.name,
        "membership_type": type(customer).__name__.replace(
            "Customer", ""
        ),
        "max_items": customer.max_items,
        "unpaid_fines": gearshare.get_unpaid_fines(customer_id),
        "active": [
            {
                "rental_id": rental.rental_id,
                "item": gearshare.items[rental.sku].name,
                "due_date": rental.due_date.isoformat(),
                "days_overdue": rental.days_late(gearshare.today),
            }
            for rental in active_rentals
        ],
    }


# --------------------------------------------------
# GLOBAL EXCEPTION HANDLERS
# --------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request, exc):

    if isinstance(exc.detail, dict) and "error" in exc.detail:
        content = exc.detail
    else:
        content = {
            "error": "HTTPException",
            "message": str(exc.detail),
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request, exc):

    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request data.",
        },
    )
