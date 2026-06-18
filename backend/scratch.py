"""
Phase 1 — Python crash-course for a PHP/JS developer.

Run me:   cd backend && uv run python scratch.py

This file is a guided tour. Read top-to-bottom, run it, then do the 3 TODO
exercises at the bottom. Nothing here is part of the real app — it's a sandbox.
"""

from __future__ import annotations  # lets us use modern type-hint syntax everywhere

import asyncio  # Python's built-in async runtime (no external lib needed)


# ----------------------------------------------------------------------------
# 1. Variables, f-strings, and TYPE HINTS
# ----------------------------------------------------------------------------
# PHP: $name = "Dilip";   JS: const name = "Dilip";
# Python has no $ and no const/let — just a name. Type hints (": str") are
# OPTIONAL annotations: Python does NOT enforce them at runtime, but FastAPI,
# editors, and ruff all use them heavily. Treat them as required in this project.

name: str = "Dilip"
age: int = 30

# f-strings = string interpolation. PHP "Hi $name" / JS `Hi ${name}` -> f"Hi {name}"
print(f"1) Hi {name}, you are {age} — next year {age + 1}.")


# ----------------------------------------------------------------------------
# 2. Functions with typed params + return type
# ----------------------------------------------------------------------------
# `def` defines a function. "-> str" is the return type. Indentation (4 spaces)
# defines the body — there are NO curly braces in Python. Blocks end by dedent.

def greet(person: str, excited: bool = False) -> str:
    suffix = "!" if excited else "."   # ternary: <value_if_true> if <cond> else <value_if_false>
    return f"Hello, {person}{suffix}"

print("2)", greet("world"), greet("Python", excited=True))


# ----------------------------------------------------------------------------
# 3. Lists & dicts (≈ JS arrays & objects / PHP arrays)
# ----------------------------------------------------------------------------
roles: list[str] = ["user", "assistant", "system"]
message: dict[str, str] = {"role": "user", "content": "Hi there"}

print("3)", roles[0], "->", message["content"])

# COMPREHENSIONS — a Python superpower. Build a new list inline.
# JS: roles.map(r => r.upper())   ->   [r.upper() for r in roles]
upper_roles = [r.upper() for r in roles]
print("   comprehension:", upper_roles)


# ----------------------------------------------------------------------------
# 4. async / await  (this is what FastAPI + OpenAI calls use)
# ----------------------------------------------------------------------------
# Just like JS: `async def` declares a coroutine, `await` waits for one.
# Difference from JS: calling an async function does NOT start it — you must
# `await` it (or hand it to the event loop). asyncio.run(...) starts the loop.

async def fetch_fake_reply(prompt: str) -> str:
    await asyncio.sleep(0.2)            # pretend this is a network call to OpenAI
    return f"(echo) {prompt}"

async def main() -> None:
    reply = await fetch_fake_reply("stream me")
    print("4)", reply)

asyncio.run(main())  # entry point that drives the async code above


# ----------------------------------------------------------------------------
# 5. GENERATORS with `yield`  (the basis of streaming responses later)
# ----------------------------------------------------------------------------
# A function with `yield` returns lazily, one item at a time, instead of
# building a whole list. In Phase 5/6 the OpenAI stream is consumed this way.

def token_stream(sentence: str):
    for word in sentence.split():
        yield word          # hands one word back to the caller, then pauses here

print("5) streamed:", end=" ")
for token in token_stream("tokens arrive one by one"):
    print(token, end="|")
print()


# ============================================================================
# YOUR EXERCISES  (delete the `pass` lines and make the asserts pass)
# Run again after each: `uv run python scratch.py`
# ============================================================================
print("\n--- exercises ---")

# Exercise A: write a typed function `double(n: int) -> int` that returns n * 2.
# TODO: define double(...) here
def double(n: int) -> int:
    return n * 2

assert double(21) == 42, "Exercise A not done yet"
print("A) ok")

# Exercise B: use a list comprehension to build squares of 1..5 -> [1,4,9,16,25]
# Hint: range(1, 6) yields 1,2,3,4,5
squares: list[int] = [n * n for n in range(1, 6)]  # TODO: replace [] with a comprehension
assert squares == [1, 4, 9, 16, 25], "Exercise B not done yet"
print("B) ok")

# Exercise C: write an async function `slow_add(a, b)` that awaits asyncio.sleep(0)
# and returns a + b. Then await it inside main_exercise().
async def slow_add(a: int, b: int) -> int:
    await asyncio.sleep(0)
    return a + b

async def main_exercise() -> None:
    result = await slow_add(2, 3)
    assert result == 5, "Exercise C not done yet"
    print("C) ok")

asyncio.run(main_exercise())

print("\nAll exercises passed! Phase 1 checkpoint complete. ✅")
