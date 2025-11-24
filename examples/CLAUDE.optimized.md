# CLAUDE.md

## Project Overview
### Computer-Use Demo
#### Setup & Development
Preserve the existing instructions for setup and development. However, provide more explicit details:
- **Setup environment**: `./setup.sh` to set up the environment for the demo.
- **Build Docker**: `docker build . -t computer-use-demo:local` to build the Docker image.
- **Run container**: `docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -v $(pwd)/computer_use_demo:/home/computeruse/computer_use_demo/ -v $HOME/.anthropic:/home/computeruse/.anthropic -p 5900:5900 -p 8501:8501 -p 6080:6080 -p 8080:8080 -it computer-use-demo:local` to run the container.
- **Run test**: `pytest tests/path_to_test.py::test_name -v` to run a specific test.

#### Testing & Code Quality
Enhance testing and code quality instructions with concrete examples:
- **Lint**: Use `ruff check .` to lint the code. Run `ruff format .` to format the code.
- **Typecheck**: Use `pyright` to typecheck the code. Ensure all functions have type annotations.
- **Run tests**: Use `pytest` to run all tests. For a specific test, use `pytest tests/path_to_test.py::test_name -v`.
- **Code review process**: Implement a weekly code review using tools like GitHub Code Review.

#### Code Style
Enhance code style with more specific guidelines:
- **Python**: Use snake_case for functions and variables, and PascalCase for classes. Use type annotations for all parameters and returns.
- **Imports**: Use `isort` with combine-as-imports to format imports.
- **Error handling**: Use custom ToolError for tool errors.

### Customer Support Agent
#### Setup & Development
Preserve the existing instructions for setup and development:
- **Install dependencies**: `npm install` to install dependencies.
- **Run dev server**: `npm run dev` (full UI) to start the development server.
- **UI variants**: `npm run dev:left` (left sidebar), `npm run dev:right` (right sidebar), `npm run dev:chat` (chat only) to run different UI variants.
- **Lint**: Use `npm run lint` to lint the code.
- **Build**: `npm run build` (full UI).

#### Code Style
Enhance code style with more specific guidelines:
- **TypeScript**: Use strict mode with proper interfaces. Follow ESLint Next.js configuration for formatting.
- **Components**: Use function components with React hooks. Use shadcn/ui components library for UI components.

## Financial Data Analyst
#### Setup & Development
Preserve the existing instructions for setup and development:
- **Install dependencies**: `npm install` to install dependencies.
- **Run dev server**: `npm run dev` to start the development server.
- **Lint**: Use `npm run lint` to lint the code.
- **Build**: `npm run build`

#### Code Style
Enhance code style with more specific guidelines:
- **TypeScript**: Use strict mode with proper type definitions. Use React hooks for state management.

### Concrete Examples and Commands
Add concrete examples where needed to enhance actionability:
- For the Computer-Use Demo, provide an example of how to run a test using `pytest tests/path_to_test.py::test_name -v`.
- For the Customer Support Agent, provide an example of how to use the UI variants.

### Project Structure and Architecture
Provide more project structure and architecture information to enhance context:
#### Directory Structure
The project follows the standard Node.js directory structure. The main components are organized into separate directories for each application.
#### Component Interaction
Components interact with each other using RESTful APIs. For example, the UI component sends requests to the backend API to retrieve data.

### Project Overview
This CLAUDE.md file has been improved to address weaknesses and recommendations. It now includes more explicit instructions, concrete examples, and specific guidelines for code style and testing.