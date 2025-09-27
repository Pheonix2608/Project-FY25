# Contributing to the Intelligent Chatbot Project

First off, thank you for considering contributing to this project! We welcome all contributions, from bug reports and feature requests to code and documentation updates. This guide will help you get started.

## How to Contribute

We use a standard GitHub flow for contributions. Here’s a summary of the process:

1.  **Fork the Repository**: Start by forking the project to your own GitHub account.
2.  **Clone Your Fork**: Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/YOUR_USERNAME/Project-FY25.git
    cd Project-FY25
    ```
3.  **Create a Feature Branch**: Create a descriptive branch for your changes.
    ```bash
    git checkout -b feature/your-awesome-feature
    ```
4.  **Make Your Changes**: Write your code, fix bugs, or improve the documentation.
5.  **Run Tests**: Ensure all existing tests pass and add new ones for your features.
    ```bash
    pytest
    ```
6.  **Commit Your Changes**: Use clear and descriptive commit messages. We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
    ```bash
    git commit -m "feat: Add a new response personalization feature"
    ```
7.  **Push to Your Fork**: Push your changes to your forked repository.
    ```bash
    git push origin feature/your-awesome-feature
    ```
8.  **Open a Pull Request**: Go to the original repository and open a pull request from your feature branch. Provide a clear description of your changes and reference any related issues.

## Development Setup

To ensure a consistent development environment, please follow the setup instructions in the main [README.md](./ReadME.md) file. This includes setting up a virtual environment and installing all required dependencies.

## Coding Standards

Please adhere to the following standards to maintain code quality and consistency:

-   **Style Guide**: We follow the **PEP 8** style guide for Python code.
-   **Docstrings**: All public modules, classes, functions, and methods must have Google-style docstrings. Our codebase is now fully documented, so you can refer to existing files for examples.
-   **Naming Conventions**: Use `snake_case` for variables and functions, and `PascalCase` for classes.
-   **Imports**: Organize imports at the top of the file, grouped into standard library, third-party, and local application imports.

For more details, refer to the `docs/coding_standards.md` file.

## Submitting a Pull Request

When you open a pull request, please ensure the following:
-   Your PR has a clear and descriptive title.
-   The PR description explains the "what" and "why" of your changes.
-   You have linked any relevant GitHub issues (e.g., "Closes #123").
-   You have run all tests and they are passing.
-   You have updated the documentation (`README.md`, `docs/`, etc.) if your changes affect it.
-   You have updated `CHANGELOG.md` and `IMPROVEMENTS.md` with a summary of your contribution.

## Reporting Bugs and Requesting Features

Use GitHub Issues to report bugs or request new features. Please use the provided issue templates and include as much detail as possible:
-   **For Bugs**: Steps to reproduce, expected behavior, actual behavior, and any relevant logs or screenshots.
-   **For Features**: A clear description of the proposed feature and why it would be valuable to the project.

Thank you for helping us make this project better!