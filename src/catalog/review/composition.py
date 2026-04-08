"""Composition root для модуля отзывов."""

from src.catalog.review.application.commands.create_review import CreateReviewCommand
from src.catalog.review.application.commands.delete_review import DeleteReviewCommand
from src.catalog.review.application.commands.update_review import UpdateReviewCommand
from src.catalog.review.application.queries.review_admin_queries import ReviewAdminQueries
from src.catalog.review.application.queries.review_queries import ReviewQueries
from src.catalog.review.container import container


class ReviewComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateReviewCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateReviewCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteReviewCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(ReviewQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(ReviewAdminQueries, db=db)
