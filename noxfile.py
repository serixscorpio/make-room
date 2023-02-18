from nox_poetry import Session, session

@session(name="pre-commit", python="3.10")
def precommit(session: Session) -> None:
    """Lint using pre-commit."""
    args = session.posargs or ["run", "--all-files", "--show-diff-on-failure"]
    session.install(
        "bandit",
        "black",
        "flake8",
        "pre-commit"
    )
    session.run("pre-commit", *args)
    