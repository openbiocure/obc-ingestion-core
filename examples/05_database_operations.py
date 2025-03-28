"""
Database Operations Example

This example demonstrates how to perform more advanced
database operations using the repository pattern.
"""
import asyncio
from typing import Optional, List, Protocol
from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, func

from src import engine
from src.data.entity import BaseEntity
from src.data.repository import IRepository, Repository
from src.data.specification import Specification
from src.data.db_context import DbContext, IDbContext

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
    async def publish(self, post_id: str) -> Optional[Post]: ...

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

# Repository implementations
class UserRepository(Repository[User], IUserRepository):
    def __init__(self, session):
        super().__init__(session, User)
    
    async def find_by_username(self, username: str) -> Optional[User]:
        return await self.find_one(UserByUsernameSpecification(username))
    
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one(UserByEmailSpecification(email))
    
    async def find_one(self, spec: Specification[User]) -> Optional[User]:
        results = await self.find(spec)
        return results[0] if results else None

class PostRepository(Repository[Post], IPostRepository):
    def __init__(self, session):
        super().__init__(session, Post)
    
    async def find_by_user_id(self, user_id: str) -> List[Post]:
        return await self.find(PostByUserIdSpecification(user_id))
    
    async def find_published(self) -> List[Post]:
        return await self.find(PublishedPostSpecification())
    
    async def publish(self, post_id: str) -> Optional[Post]:
        return await self.update(post_id, published=True)

async def main():
    # Initialize and start the engine
    engine.initialize()
    engine.start()
    
    # Get database context
    db_context = engine.resolve(IDbContext)
    await db_context.initialize()
    
    # Create database tables
    async with db_context.begin_transaction():
        await db_context.execute(BaseEntity.metadata.create_all(bind=db_context._engine))
    
    # Create repositories
    user_repo = UserRepository(db_context.get_session())
    post_repo = PostRepository(db_context.get_session())
    
    # Register repositories
    engine.register(IUserRepository, user_repo)
    engine.register(IPostRepository, post_repo)
    
    # Resolve repositories
    user_repository = engine.resolve(IUserRepository)
    post_repository = engine.resolve(IPostRepository)
    
    print("Database Operations Example:")
    print("===========================")
    
    # Create a user
    user = await user_repository.create(
        username="johndoe",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe"
    )
    print(f"\nCreated user: {user.first_name} {user.last_name} ({user.username})")
    
    # Create some posts
    post1 = await post_repository.create(
        title="First Post",
        content="This is my first post!",
        published=False,
        user_id=user.id
    )
    
    post2 = await post_repository.create(
        title="Second Post",
        content="This is my second post!",
        published=False,
        user_id=user.id
    )
    
    print(f"\nCreated posts: {post1.title}, {post2.title}")
    
    # Publish a post
    published_post = await post_repository.publish(post1.id)
    print(f"\nPublished post: {published_post.title}")
    
    # Find posts by user
    user_posts = await post_repository.find_by_user_id(user.id)
    print(f"\nUser has {len(user_posts)} posts:")
    for post in user_posts:
        status = "Published" if post.published else "Draft"
        print(f"- {post.title} ({status})")
    
    # Find published posts
    published_posts = await post_repository.find_published()
    print(f"\nPublished posts: {len(published_posts)}")
    
    # Find user by username
    found_user = await user_repository.find_by_username("johndoe")
    if found_user:
        print(f"\nFound user by username: {found_user.first_name} {found_user.last_name}")
    
    # Cleanup
    await db_context.close()
    print("\nDatabase cleanup complete")

if __name__ == "__main__":
    asyncio.run(main())
