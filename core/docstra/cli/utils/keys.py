def ensure_api_keys(self, model_provider: str) -> bool:
    """Ensure necessary API keys are available or prompt for them.

    Args:
        model_provider: The model provider to check keys for

    Returns:
        True if keys are available or were successfully set, False otherwise
    """
    import os
    from rich.prompt import Prompt
    from pathlib import Path

    # Create .docstra dir if it doesn't exist
    docstra_dir = Path(self.working_dir) / ".docstra"
    docstra_dir.mkdir(exist_ok=True, parents=True)

    # Set up .env file
    env_file = docstra_dir / ".env"
    if not env_file.exists():
        env_file.touch()
    else:
        # Load existing .env
        from dotenv import load_dotenv

        load_dotenv(env_file)

        # Ensure file ends with newline for appending
        content = env_file.read_text()
        if content and not content.endswith("\n"):
            with open(env_file, "a") as f:
                f.write("\n")

    # Check for required keys based on provider
    if model_provider.lower() == "openai" and not os.environ.get("OPENAI_API_KEY"):
        self.console.print("[yellow]OpenAI API key not found in environment.[/yellow]")
        openai_key = Prompt.ask("Enter your OpenAI API key", password=True, default="")
        if openai_key:
            with open(env_file, "a") as f:
                f.write(f"OPENAI_API_KEY={openai_key}\n")
            os.environ["OPENAI_API_KEY"] = openai_key

            # Reload env vars
            from dotenv import load_dotenv

            load_dotenv(env_file)

            self.console.print(
                "[green]OpenAI API key saved to .docstra/.env file[/green]"
            )
            return True
        else:
            self.console.print(
                "[red]No API key provided. Some operations may fail.[/red]"
            )
            return False

    elif model_provider.lower() == "anthropic" and not os.environ.get(
        "ANTHROPIC_API_KEY"
    ):
        self.console.print(
            "[yellow]Anthropic API key not found in environment.[/yellow]"
        )
        anthropic_key = Prompt.ask(
            "Enter your Anthropic API key", password=True, default=""
        )
        if anthropic_key:
            with open(env_file, "a") as f:
                f.write(f"ANTHROPIC_API_KEY={anthropic_key}\n")
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

            # Reload env vars
            from dotenv import load_dotenv

            load_dotenv(env_file)

            self.console.print(
                "[green]Anthropic API key saved to .docstra/.env file[/green]"
            )
            return True
        else:
            self.console.print(
                "[red]No API key provided. Some operations may fail.[/red]"
            )
            return False

    # If we get here, either the needed keys are already set or we don't recognize the provider
    return True
