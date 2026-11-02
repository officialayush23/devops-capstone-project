"""
Models for Account.

All of the models are stored in this module.
"""
import logging
from datetime import date

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# SQLAlchemy object initialized later by init_db().
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing."""


def init_db(app):
    """Initialize the SQLAlchemy application."""
    Account.init_db(app)


class PersistentBase:
    """Base class providing persistent database methods."""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """Create an Account in the database."""
        logger.info("Creating %s", self.name)
        self.id = None
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update an Account in the database."""
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Remove an Account from the database."""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initialize the database session and create tables."""
        logger.info("Initializing database")
        cls.app = app
        db.init_app(app)

        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls):
        """Return all records from the database."""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Find a record by its ID."""
        logger.info("Processing lookup for id %s", by_id)
        return cls.query.get(by_id)


class Account(db.Model, PersistentBase):
    """Class representing an Account."""

    app = None

    # Table schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    address = db.Column(db.String(256))
    phone_number = db.Column(db.String(32), nullable=True)
    date_joined = db.Column(
        db.Date(),
        nullable=False,
        default=date.today,
    )

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serialize an Account into a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserialize an Account from a dictionary.

        Args:
            data (dict): Dictionary containing Account data.

        Raises:
            DataValidationError: If the supplied data is invalid.
        """
        if not isinstance(data, dict):
            raise DataValidationError(
                "Invalid Account: request body must be a JSON object."
            )

        try:
            self.name = data["name"]
            self.email = data["email"]
            self.address = data["address"]
            self.phone_number = data.get("phone_number")

            date_joined = data.get("date_joined")

            if date_joined:
                self.date_joined = date.fromisoformat(date_joined)
            else:
                self.date_joined = date.today()

        except KeyError as error:
            raise DataValidationError(
                "Invalid Account: missing " + error.args[0]
            ) from error

        except (TypeError, ValueError) as error:
            raise DataValidationError(
                "Invalid Account: invalid field value - " + str(error)
            ) from error

        return self

    @classmethod
    def find_by_name(cls, name):
        """Return all Accounts with the given name."""
        logger.info("Processing name query for %s", name)
        return cls.query.filter(cls.name == name)
