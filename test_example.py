import asyncio

from server import run_quality_assurance


if __name__ == "__main__":
    asyncio.run(run_quality_assurance("examples/langwatch_blog.md"))
