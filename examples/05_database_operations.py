"""
Database Operations Example

This example demonstrates how to perform more advanced
database operations using the repository pattern with entities.
"""

import asyncio
import uuid
from typing import Optional, List, Protocol
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from openbiocure_corelib import engine
from openbiocure_corelib.data.entity import BaseEntity
from openbiocure_corelib.data.repository import IRepository
from openbiocure_corelib.data.specification import Specification


# Define entities
class User(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)


class Post(BaseEntity):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    published: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))


# Define repository interfaces
class IUserRepository(IRepository[User], Protocol):
    async def find_by_username(self, username: str) -> Optional[User]: ...
    async def find_by_email(self, email: str) -> Optional[User]: ...


class IPostRepository(IRepository[Post], Protocol):
    async def find_by_user_id(self, user_id: str) -> List[Post]: ...
    async def find_published(self) -> List[Post]: ...
    async def publish(self, post: Post) -> Post: ...


# Define specifications
class UserByUsernameSpecification(Specification[User]):
    def __init__(self, username: str):
        self.username = username

    def to_expression(self):
        return User.username == self.username


class UserByEmailSpecification(Specification[User]):
    def __init__(self, email: str):
        self.email = email

    def to_expression(self):
        return User.email == self.email


class PostByUserIdSpecification(Specification[Post]):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def to_expression(self):
        return Post.user_id == self.user_id


class PublishedPostSpecification(Specification[Post]):
    def to_expression(self):
        return Post.published == True


async def main():
    # Initialize and start the engine
    engine.initialize()
    await engine.start()

    # Resolve repositories
    user_repository = engine.resolve(IUserRepository)
    post_repository = engine.resolve(IPostRepository)

    print("Database Operations Example:")
    print("===========================")

    # Create a user entity with unique data
    unique_id = str(uuid.uuid4())
    user = User(
        id=unique_id,
        username=f"johndoe_{unique_id[:8]}",
        email=f"john.doe_{unique_id[:8]}@example.com",
        first_name="John",
        last_name="Doe",
    )

    # Save the user
    created_user = await user_repository.create(user)
    print(
        f"\nCreated user: {created_user.first_name} {created_user.last_name} ({created_user.username})"
    )

    # Create post entities
    post1 = Post(
        id=str(uuid.uuid4()),
        title="First Post",
        content="This is my first post!",
        published=False,
        user_id=created_user.id,
    )

    post2 = Post(
        title="Second Post",
        content="This is my second post!",
        published=False,
        user_id=created_user.id,
    )

    # Save posts
    created_post1 = await post_repository.create(post1)
    created_post2 = await post_repository.create(post2)

    print(f"\nCreated posts: {created_post1.title}, {created_post2.title}")

    # Publish a post
    created_post1.published = True
    published_post = await post_repository.update(created_post1)
    print(f"\nPublished post: {published_post.title}")

    # Find posts by user
    user_posts = await post_repository.find(PostByUserIdSpecification(created_user.id))
    print(f"\nUser has {len(user_posts)} posts:")
    for post in user_posts:
        status = "Published" if post.published else "Draft"
        print(f"- {post.title} ({status})")

    # Find published posts
    published_posts = await post_repository.find(PublishedPostSpecification())
    print(f"\nPublished posts: {len(published_posts)}")

    # Find user by username
    found_user = await user_repository.find_one(
        UserByUsernameSpecification(created_user.username)
    )
    if found_user:
        print(
            f"\nFound user by username: {found_user.first_name} {found_user.last_name}"
        )


if __name__ == "__main__":
    asyncio.run(main())
