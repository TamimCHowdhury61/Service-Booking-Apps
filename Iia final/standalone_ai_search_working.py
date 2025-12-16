#!/usr/bin/env python3
"""
Standalone AI Search Tool - GOOGLE GENAI VERSION
Works like a normal chatbot using Gemini via the google-genai SDK.
Falls back to lightweight mock responses if the SDK/API is unavailable.
"""

from __future__ import annotations

import os
import sys
from typing import Optional, List, Dict

import json
import time

try:
    # New official SDK
    from google import genai
except ImportError:
    genai = None  # We will fall back to mock mode if this is missing


class StandaloneAISearch:
    """Simple standalone AI search tool using Gemini with fallback."""

    def __init__(self, use_fallback: bool = False):
        # Prefer environment variable; fall back to hardcoded placeholder
        self.api_key: str = os.getenv("GOOGLE_API_KEY", "AIzaSyDYvtoPhcz14Mp_ib8wPOS7zYxbT6aeHDQ")
        # Use any valid Gemini model you have access to
        self.model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self.conversation_history: List[Dict[str, str]] = []
        self.max_tokens: int = 1024
        self.temperature: float = 0.7

        # Explicit fallback flag (--mock) and runtime health flag
        self.use_fallback: bool = use_fallback
        self.api_working: Optional[bool] = None

        # SDK client
        self.client = None
        if not self.use_fallback and genai is not None and self.api_key and self.api_key != "apikey":
            try:
                self.client = genai.Client(api_key=self.api_key)
                # Light sanity check
                _ = self.client.models.generate_content(
                    model=self.model,
                    contents="Hello! Please respond with a short greeting."
                )
                self.api_working = True
            except Exception as e:  # noqa: BLE001
                # If anything fails here, we’ll fall back to mock mode
                print(f"[WARN] Could not initialize google-genai client: {e}")
                self.client = None
                self.api_working = False
        else:
            if genai is None:
                print("[WARN] google-genai SDK not installed. Using mock responses.")
            elif not self.api_key or self.api_key == "apikey":
                print("[WARN] GOOGLE_API_KEY not set (or still 'apikey'). Using mock responses.")
            if self.use_fallback:
                print("[INFO] Mock mode enabled via --mock.")
            self.api_working = False

    # ----------------- Fallback / Mock -----------------

    def _get_mock_response(self, user_input: str) -> str:
        """Get mock response when API is down or in --mock mode."""
        # Very simple keyword-based helper; you can extend this as you like.
        queries = {
            "plumber": (
                "Based on your needs for plumbing service, I can recommend local professional plumbers. "
                "They typically charge $50–75/hour for residential services. Common issues include leak "
                "detection, pipe repair, and drain cleaning. Would you like more specific recommendations?"
            ),
            "electrician": (
                "For electrical services, certified electricians in your area can help with wiring, "
                "circuit repair, and safety inspections. Typical rates are $60–85/hour. Emergency services "
                "may have additional charges. Do you have a specific electrical problem?"
            ),
            "carpenter": (
                "Professional carpenters offer custom woodwork, furniture repair, and installation services. "
                "Hourly rates typically range from $50–70. What type of carpentry work do you need?"
            ),
            "painter": (
                "Professional painters provide interior and exterior painting services. Rates vary from "
                "$30–60/hour depending on project complexity. What's your painting project about?"
            ),
            "hvac": (
                "HVAC technicians handle heating, cooling, and ventilation system repairs and maintenance. "
                "Professional rates are typically $75–100/hour. Do you need repairs or maintenance?"
            ),
            "cleaning": (
                "Professional cleaning services range from $25–50/hour depending on the type of cleaning. "
                "What cleaning service do you need?"
            ),
        }

        user_lower = user_input.lower()
        for key, response in queries.items():
            if key in user_lower:
                return response

        # Generic fallback for any topic
        return (
            "I’m currently running in mock/offline mode, so I can’t access the real Gemini model.\n\n"
            "However, you can still ask general questions (technology, programming, science, etc.) and I’ll try "
            "to give a simple heuristic answer. If you want full AI answers, make sure:\n"
            "1. `pip install google-genai`\n"
            "2. Set a valid `GOOGLE_API_KEY` in your environment.\n"
        )

    

    def _build_chat_prompt(self, user_input: str, system_prompt: Optional[str]) -> str:
        """
        Build a single text prompt containing prior conversation + current input.
        This avoids fiddly structured Content objects and keeps things robust.
        """
        parts: List[str] = []

        if system_prompt:
            parts.append(f"System: {system_prompt}\n")

        if self.conversation_history:
            parts.append("Conversation so far:\n")
            for msg in self.conversation_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                parts.append(f"{role}: {msg['content']}\n")

        parts.append(f"User: {user_input}\nAssistant:")

        return "\n".join(parts)

    def query(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a query to Gemini and get response.

        Args:
            user_input: The user's question/search query.
            system_prompt: Optional system instruction for the AI.

        Returns:
            str: The AI response.
        """

        # If we’re in forced fallback mode or the SDK/API is not working, use mock.
        if self.use_fallback or self.api_working is False or self.client is None:
            return self._get_mock_response(user_input)

        # Default system prompt for general assistant behavior
        if not system_prompt:
            system_prompt = (
                "You are a helpful, concise AI assistant. Answer the user's question clearly and directly. "
                "If code is requested, provide runnable examples."
            )

        prompt = self._build_chat_prompt(user_input, system_prompt)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                },
            )

            # SDK returns a GenerateContentResponse; .text gives full concatenated text
            ai_response = getattr(response, "text", None) or "Error: Empty response from Gemini."

            # Update history for next turn
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            self.api_working = True
            return ai_response

        except Exception as e:  # noqa: BLE001
            # On any error, mark API as broken and fall back
            self.api_working = False
            return f"⚠️  Gemini API error: {e}\n\n" + self._get_mock_response(user_input)

    # ----------------- Small helpers -----------------

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def search(self, query: str) -> str:
        """Alias for query()."""
        return self.query(query)

    # ----------------- CLI / Interactive -----------------

    def interactive_mode(self) -> None:
        """Run in interactive mode - chat with the AI."""
        print("=" * 70)
        print("🤖 STANDALONE AI SEARCH (Gemini via google-genai)")
        print("=" * 70)
        print("\n💡 Ask me anything. Examples:")
        print("   - How do I fix a leaking sink?")
        print("   - Explain multithreading in Python.")
        print("   - Help me design a database schema.\n")
        print("Commands: 'quit' to exit, 'clear' to reset, 'mock' to force mock mode, 'api' to try real API.\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue

                cmd = user_input.lower()
                if cmd == "quit":
                    print("\n👋 Goodbye!")
                    break
                if cmd == "clear":
                    self.clear_history()
                    print("🔄 Conversation history cleared.\n")
                    continue
                if cmd == "mock":
                    self.use_fallback = True
                    self.api_working = False
                    print("🎭 Switched to mock response mode.\n")
                    continue
                if cmd == "api":
                    self.use_fallback = False
                    # Re-init client if possible
                    if genai is not None and self.api_key and self.api_key != "apikey":
                        try:
                            self.client = genai.Client(api_key=self.api_key)
                            self.api_working = True
                            print("🔌 Switched to Gemini API mode.\n")
                        except Exception as e:  # noqa: BLE001
                            print(f"[WARN] Could not re-init API client: {e}")
                            self.api_working = False
                    else:
                        print("⚠️ google-genai not installed or API key missing. Still in mock mode.\n")
                    continue

                print("\n🤔 Thinking...\n")
                response = self.query(user_input)
                print(f"AI: {response}\n")
                print("-" * 70 + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:  # noqa: BLE001
                print(f"Error: {e}")


def main() -> None:
    """Main entry point."""

    # Check for command line flags
    use_fallback = "--mock" in sys.argv

    ai = StandaloneAISearch(use_fallback=use_fallback)

    # Remove flags from argv for parsing
    argv_clean = [arg for arg in sys.argv if not arg.startswith("--")]

    # If there’s a CLI query, run once; else interactive
    if len(argv_clean) > 1:
        query_text = " ".join(argv_clean[1:])
        print("=" * 70)
        print("🤖 STANDALONE AI SEARCH (Gemini via google-genai)")
        print("=" * 70)
        print(f"\n📝 Your Query: {query_text}\n")
        print("🤔 Getting response...\n")

        response = ai.query(query_text)
        print(f"🔍 Response:\n{response}\n")
    else:
        ai.interactive_mode()


if __name__ == "__main__":
    main()
