"""
Account Service

This microservice handles the lifecycle of Accounts.
"""
from flask import jsonify, request, make_response, abort, url_for

from service.models import Account
from service.common import status
from . import app


@app.route("/health")
def health():
    """Health Status"""
    return jsonify(status="OK"), status.HTTP_200_OK


@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


@app.route("/accounts", methods=["POST"])
def create_accounts():
    """Create a new Account."""
    app.logger.info("Request to create an Account")
    check_content_type("application/json")

    account = Account()
    account.deserialize(request.get_json())
    account.create()

    location_url = url_for(
        "get_account",
        account_id=account.id,
        _external=True,
    )

    return make_response(
        jsonify(account.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/accounts", methods=["GET"])
def list_accounts():
    """List all Accounts, with optional name and email filters."""
    app.logger.info("Request to list Accounts")

    query = Account.query

    name = request.args.get("name")
    email = request.args.get("email")

    if name:
        query = query.filter(Account.name == name)

    if email:
        query = query.filter(Account.email == email)

    accounts = query.all()
    results = [account.serialize() for account in accounts]

    return jsonify(results), status.HTTP_200_OK


@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id):
    """Read an Account by its ID."""
    app.logger.info("Request to read Account with id: %s", account_id)

    account = Account.find(account_id)

    if account is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{account_id}' was not found.",
        )

    return jsonify(account.serialize()), status.HTTP_200_OK


@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """Update an existing Account."""
    app.logger.info("Request to update Account with id: %s", account_id)
    check_content_type("application/json")

    account = Account.find(account_id)

    if account is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{account_id}' was not found.",
        )

    account.deserialize(request.get_json())
    account.id = account_id
    account.update()

    return jsonify(account.serialize()), status.HTTP_200_OK


@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Delete an Account by its ID."""
    app.logger.info("Request to delete Account with id: %s", account_id)

    account = Account.find(account_id)

    if account is None:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Account with id '{account_id}' was not found.",
        )

    account.delete()

    return "", status.HTTP_204_NO_CONTENT


def check_content_type(media_type):
    """Check that the request content type is correct."""
    content_type = request.headers.get("Content-Type", "")

    if content_type.split(";")[0].strip().lower() == media_type.lower():
        return

    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
